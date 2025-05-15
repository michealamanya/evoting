from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Notification, NotificationCategory, NotificationPreference, CategoryPreference

def create_notification(recipient, title, message, category_name, priority='medium', related_object=None, link=''):
    """
    Create a notification for a user
    
    Args:
        recipient: User object - the user to notify
        title: str - notification title
        message: str - notification message
        category_name: str - category name
        priority: str - low, medium, or high
        related_object: Model instance - optional related object
        link: str - optional URL to include
        
    Returns:
        Notification object
    """
    # Get or create category
    category, _ = NotificationCategory.objects.get_or_create(name=category_name)
    
    # Check user preferences
    should_notify = True
    try:
        user_pref = NotificationPreference.objects.get(user=recipient)
        if not user_pref.in_app_notifications:
            should_notify = False
        
        # Check category preference
        try:
            category_pref = CategoryPreference.objects.get(
                user_preference=user_pref,
                category=category
            )
            if not category_pref.receive_notifications:
                should_notify = False
        except CategoryPreference.DoesNotExist:
            # If no specific preference exists, create it with default (True)
            CategoryPreference.objects.create(
                user_preference=user_pref,
                category=category,
                receive_notifications=True
            )
    except NotificationPreference.DoesNotExist:
        # Create default preferences for user
        user_pref = NotificationPreference.objects.create(user=recipient)
        CategoryPreference.objects.create(
            user_preference=user_pref,
            category=category,
            receive_notifications=True
        )
    
    if not should_notify:
        return None
    
    # Create notification
    notification = Notification(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        priority=priority,
        link=link
    )
    
    # Add related object if provided
    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        notification.content_type = content_type
        notification.object_id = related_object.id
    
    notification.save()
    return notification

def get_unread_count(user):
    """Get count of unread notifications for a user"""
    return Notification.objects.filter(recipient=user, is_read=False).count()
