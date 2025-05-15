from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from electronic_voting.models import Election, Position, Candidate, Vote
from user_management.models import UserProfile, UserActivity

@staff_member_required
def analytics_dashboard(request):
    # Get summary statistics
    elections_count = Election.objects.count()
    active_elections = Election.objects.filter(is_active=True).count()
    total_votes = Vote.objects.count()
    total_users = UserProfile.objects.count()
    
    # Recent votes
    recent_votes = Vote.objects.select_related('voter', 'candidate', 'position', 'election').order_by('-timestamp')[:10]
    
    # Elections with highest participation
    elections_by_participation = Election.objects.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count')[:5]
    
    # Recent activities
    recent_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Ongoing elections
    now = timezone.now()
    ongoing_elections = Election.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        is_active=True
    )
    
    return render(request, 'analytics/dashboard.html', {
        'elections_count': elections_count,
        'active_elections': active_elections,
        'total_votes': total_votes,
        'total_users': total_users,
        'recent_votes': recent_votes,
        'elections_by_participation': elections_by_participation,
        'recent_activities': recent_activities,
        'ongoing_elections': ongoing_elections,
    })

@staff_member_required
def election_analytics(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    
    # Get all positions for this election
    positions = Position.objects.filter(election=election)
    
    # Vote counts by position
    position_data = []
    for position in positions:
        candidates = Candidate.objects.filter(position=position)
        candidate_data = []
        
        for candidate in candidates:
            vote_count = Vote.objects.filter(
                candidate=candidate,
                position=position,
                election=election
            ).count()
            
            candidate_data.append({
                'name': f"{candidate.user.first_name} {candidate.user.last_name}",
                'votes': vote_count
            })
        
        position_data.append({
            'position': position.title,
            'candidates': candidate_data
        })
    
    # Voting timeline data (votes per day)
    timeline_data = []
    if election.start_date and election.end_date:
        current_date = election.start_date.date()
        end_date = min(election.end_date.date(), timezone.now().date())
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = Vote.objects.filter(
                election=election,
                timestamp__date=current_date
            ).count()
            
            timeline_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'votes': count
            })
            
            current_date = next_date
    
    # Total votes cast in this election
    total_votes = Vote.objects.filter(election=election).count()
    
    # Percentage of eligible voters who voted (if we track total eligible)
    # This is a placeholder calculation assuming all users are eligible
    total_eligible = UserProfile.objects.count()
    participation_rate = (total_votes / total_eligible * 100) if total_eligible > 0 else 0
    
    return render(request, 'analytics/election_analytics.html', {
        'election': election,
        'position_data': position_data,
        'timeline_data': timeline_data,
        'total_votes': total_votes,
        'participation_rate': participation_rate,
    })

@staff_member_required
def voter_demographics(request):
    # Count by verification status
    verification_stats = {
        'verified': UserProfile.objects.filter(is_verified=True).count(),
        'unverified': UserProfile.objects.filter(is_verified=False).count(),
    }
    
    # Count users who have voted at least once
    voters = UserProfile.objects.filter(user__votes__isnull=False).distinct().count()
    non_voters = UserProfile.objects.filter(user__votes__isnull=True).count()
    
    voting_stats = {
        'voters': voters,
        'non_voters': non_voters,
    }
    
    # Count by registration date (last 7 days, last 30 days, older)
    now = timezone.now()
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    
    registration_stats = {
        'last_week': UserProfile.objects.filter(user__date_joined__gte=last_week).count(),
        'last_month': UserProfile.objects.filter(
            user__date_joined__gte=last_month,
            user__date_joined__lt=last_week
        ).count(),
        'older': UserProfile.objects.filter(user__date_joined__lt=last_month).count(),
    }
    
    return render(request, 'analytics/voter_demographics.html', {
        'verification_stats': verification_stats,
        'voting_stats': voting_stats,
        'registration_stats': registration_stats,
    })

@staff_member_required
def participation_trends(request):
    # Prepare data for participation over time
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    # Daily participation for the last 30 days
    daily_participation = []
    current_date = last_month.date()
    
    while current_date <= now.date():
        vote_count = Vote.objects.filter(timestamp__date=current_date).count()
        daily_participation.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'votes': vote_count
        })
        current_date += timedelta(days=1)
    
    # Participation by election
    elections = Election.objects.all()
    election_participation = []
    
    for election in elections:
        votes = Vote.objects.filter(election=election).count()
        election_participation.append({
            'election': election.title,
            'votes': votes
        })
    
    # Participation rate over different elections
    participation_rates = []
    total_users = UserProfile.objects.count()
    
    for election in elections:
        votes = Vote.objects.filter(election=election).values('voter').distinct().count()
        rate = (votes / total_users * 100) if total_users > 0 else 0
        participation_rates.append({
            'election': election.title,
            'rate': rate
        })
    
    return render(request, 'analytics/participation_trends.html', {
        'daily_participation': daily_participation,
        'election_participation': election_participation,
        'participation_rates': participation_rates,
    })

@staff_member_required
def analytics_reports(request):
    # List all elections for reporting
    elections = Election.objects.all().order_by('-start_date')
    
    # Generate summary stats for each election
    reports = []
    for election in elections:
        votes = Vote.objects.filter(election=election).count()
        unique_voters = Vote.objects.filter(election=election).values('voter').distinct().count()
        positions = Position.objects.filter(election=election).count()
        candidates = Candidate.objects.filter(position__election=election).count()
        
        # Status determination
        now = timezone.now()
        if now < election.start_date:
            status = "Upcoming"
        elif now <= election.end_date:
            status = "Ongoing"
        else:
            status = "Completed"
        
        reports.append({
            'election': election,
            'votes': votes,
            'unique_voters': unique_voters,
            'positions': positions,
            'candidates': candidates,
            'status': status
        })
    
    return render(request, 'analytics/reports.html', {
        'reports': reports,
    })
