from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q

from .models import Notification, NotificationPreference, EmailTemplate
from .forms import NotificationPreferenceForm
from electronic_voting.models import Election

@login_required
def notification_list(request):
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark as read if requested
    if 'mark_read' in request.GET:
        notifications.update(is_read=True)
        return redirect('notification_list')
    
    # Filter by type if requested
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    # Unread count
    unread_count = notifications.filter(is_read=False).count()
    
    # Get notification types for filter
    notification_types = Notification.NOTIFICATION_TYPES
    
    return render(request, 'notification/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'notification_types': notification_types,
        'current_type': notification_type,
    })

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark as read if not already
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    return render(request, 'notification/notification_detail.html', {
        'notification': notification,
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('notification_list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        messages.success(request, 'All notifications marked as read.')
        return redirect('notification_list')

@login_required
def notification_preferences(request):
    # Get or create notification preferences
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully.')
            return redirect('notification_preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    
    return render(request, 'notification/preferences.html', {
        'form': form,
    })

# Utility functions for creating notifications

def send_election_notifications(election, notification_type):
    """Send notifications to users about election events."""
    if notification_type == 'ELECTION_START':
        title = f"Election Started: {election.title}"
        message = f"The election '{election.title}' has now started and is open for voting."
        preference_field = 'election_start_notify'
    elif notification_type == 'ELECTION_END':
        title = f"Election Ended: {election.title}"
        message = f"The election '{election.title}' has ended. Results are now available."
        preference_field = 'election_end_notify'
    elif notification_type == 'RESULT_AVAILABLE':
        title = f"Results Available: {election.title}"
        message = f"The results for '{election.title}' are now available. Check them out!"
        preference_field = 'results_notify'
    else:
        return
    
    # Filter users based on their notification preferences
    query_filter = {preference_field: True}
    users_with_preferences = NotificationPreference.objects.filter(**query_filter).values_list('user_id', flat=True)
    
    # Create notifications for each user
    notifications = []
    for user_id in users_with_preferences:
        notifications.append(
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                related_election=election
            )
        )
    
    # Bulk create
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    # Send emails if needed
    # This would typically be done in an async task in production
    try:
        email_template = EmailTemplate.objects.get(name=notification_type.lower())
        for user_id in users_with_preferences:
            pref = NotificationPreference.objects.get(user_id=user_id)
            if pref.email_notifications:
                # In a real app, this would be in a background task
                user = pref.user
                send_mail(
                    email_template.subject.format(election=election.title),
                    email_template.body.format(election=election.title, user=user.username),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                )
    except EmailTemplate.DoesNotExist:
        # Log that template doesn't exist
        pass

def create_vote_confirmation(user, election, position, candidate):
    """Create a vote confirmation notification for a user."""
    # Check if user wants vote confirmations
    try:
        pref = NotificationPreference.objects.get(user=user)
        if not pref.vote_confirmation_notify:
            return
    except NotificationPreference.DoesNotExist:
        # Default to sending if preferences don't exist
        pass
    
    title = f"Vote Confirmed: {position.title}"
    message = f"Your vote for {candidate.user.get_full_name()} as {position.title} in '{election.title}' has been recorded."
    
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type='VOTE_CONFIRMATION',
        related_election=election
    )
