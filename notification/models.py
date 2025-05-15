from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from electronic_voting.models import Election

class NotificationCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Notification Categories"
    
    def __str__(self):
        return self.name

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('ELECTION_START', 'Election Started'),
        ('ELECTION_END', 'Election Ended'),
        ('VOTE_CONFIRMATION', 'Vote Confirmation'),
        ('RESULT_AVAILABLE', 'Results Available'),
        ('SYSTEM_ALERT', 'System Alert'),
        ('CUSTOM', 'Custom Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_election = models.ForeignKey(Election, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
    
    @property
    def is_recent(self):
        return (timezone.now() - self.created_at).days < 7

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    def __str__(self):
        return self.name

class CategoryPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_preferences')
    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='user_preferences')
    enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'category')
        verbose_name = "Category Preference"
        verbose_name_plural = "Category Preferences"
    
    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"{self.category.name} notifications {status} for {self.user.username}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    election_start_notify = models.BooleanField(default=True)
    election_end_notify = models.BooleanField(default=True)
    vote_confirmation_notify = models.BooleanField(default=True)
    results_notify = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
