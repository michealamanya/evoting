from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from .models import Election, Position, Candidate, Vote
from .forms import VoteForm

@login_required
def election_list(request):
    current_time = timezone.now()
    
    # Categorize elections
    upcoming_elections = Election.objects.filter(start_date__gt=current_time, is_active=True)
    ongoing_elections = Election.objects.filter(start_date__lte=current_time, end_date__gte=current_time, is_active=True)
    past_elections = Election.objects.filter(end_date__lt=current_time, is_active=True)
    
    return render(request, 'electronic_voting/election_list.html', {
        'upcoming_elections': upcoming_elections,
        'ongoing_elections': ongoing_elections,
        'past_elections': past_elections,
    })

@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    positions = election.positions.all().prefetch_related('candidates')
    
    # Check if user has already voted in this election
    user_votes = Vote.objects.filter(voter=request.user, election=election)
    voted_positions_ids = [vote.position_id for vote in user_votes]
    can_vote = election.is_ongoing
    
    return render(request, 'electronic_voting/election_detail.html', {
        'election': election,
        'positions': positions,
        'voted_positions_ids': voted_positions_ids,
        'can_vote': can_vote,
    })

@login_required
def vote_position(request, election_id, position_id):
    election = get_object_or_404(Election, pk=election_id)
    position = get_object_or_404(Position, pk=position_id, election=election)
    
    # Check if election is active and ongoing
    if not election.is_ongoing:
        messages.error(request, "This election is not currently active for voting.")
        return redirect('election_detail', election_id=election.id)
    
    # Check if user already voted for this position in this election
    if Vote.objects.filter(voter=request.user, position=position, election=election).exists():
        messages.error(request, "You have already voted for this position.")
        return redirect('election_detail', election_id=election.id)
    
    candidates = position.candidates.all()
    
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if not candidate_id:
            messages.error(request, "Please select a candidate.")
            return render(request, 'electronic_voting/vote_position.html', {
                'election': election,
                'position': position,
                'candidates': candidates
            })
        
        candidate = get_object_or_404(Candidate, pk=candidate_id, position=position)
        
        try:
            with transaction.atomic():
                Vote.objects.create(
                    voter=request.user,
                    candidate=candidate,
                    position=position,
                    election=election
                )
                messages.success(request, f"Your vote for {position.title} has been recorded!")
                return redirect('election_detail', election_id=election.id)
        except IntegrityError:
            messages.error(request, "There was an error recording your vote. You may have already voted.")
            return redirect('election_detail', election_id=election.id)
    
    return render(request, 'electronic_voting/vote_position.html', {
        'election': election,
        'position': position,
        'candidates': candidates
    })

@login_required
def vote_all(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    
    # Check if election is active and ongoing
    if not election.is_ongoing:
        messages.error(request, "This election is not currently active for voting.")
        return redirect('election_detail', election_id=election.id)
    
    # Get all positions in this election the user hasn't voted for yet
    voted_positions = Vote.objects.filter(voter=request.user, election=election).values_list('position_id', flat=True)
    positions = election.positions.exclude(id__in=voted_positions)
    
    if not positions.exists():
        messages.info(request, "You have already voted for all positions in this election.")
        return redirect('election_detail', election_id=election.id)
    
    if request.method == 'POST':
        form = VoteForm(request.POST, election=election)
        if form.is_valid():
            try:
                with transaction.atomic():
                    for field_name, candidate_id in form.cleaned_data.items():
                        if field_name.startswith('position_'):
                            position_id = int(field_name.split('_')[1])
                            position = get_object_or_404(Position, pk=position_id, election=election)
                            
                            # Skip if user already voted for this position
                            if position.id in voted_positions:
                                continue
                                
                            Vote.objects.create(
                                voter=request.user,
                                candidate=candidate_id,
                                position=position,
                                election=election
                            )
                    
                    messages.success(request, "Your votes have been recorded successfully!")
                    return redirect('election_detail', election_id=election.id)
            except IntegrityError:
                messages.error(request, "There was an error recording your votes.")
                
    else:
        form = VoteForm(election=election)
    
    return render(request, 'electronic_voting/vote_all.html', {
        'election': election,
        'form': form,
    })

@login_required
def election_results(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    positions = election.positions.all().prefetch_related('candidates__votes')
    
    # Only show results if election has ended or user is staff
    if not (election.end_date < timezone.now() or request.user.is_staff):
        messages.info(request, "Results will be available after the election ends.")
        return redirect('election_detail', election_id=election.id)
    
    results = {}
    for position in positions:
        candidates = position.candidates.all()
        results[position] = []
        for candidate in candidates:
            vote_count = candidate.votes.filter(election=election).count()
            results[position].append({
                'candidate': candidate,
                'votes': vote_count
            })
        # Sort candidates by vote count in descending order
        results[position] = sorted(results[position], key=lambda x: x['votes'], reverse=True)
    
    return render(request, 'electronic_voting/election_results.html', {
        'election': election,
        'results': results,
    })
