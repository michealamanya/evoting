from django.contrib import admin
from .models import Notification, NotificationCategory, NotificationPreference, CategoryPreference, EmailTemplate

@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Additional Information', {
            'fields': ('related_election', 'is_read', 'created_at')
        }),
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    search_fields = ('name', 'subject', 'body')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'election_start_notify', 'election_end_notify', 
                   'vote_confirmation_notify', 'results_notify')
    list_filter = ('email_notifications', 'election_start_notify', 'election_end_notify', 
                  'vote_confirmation_notify', 'results_notify')
    search_fields = ('user__username', 'user__email')

@admin.register(CategoryPreference)
class CategoryPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'enabled')
    list_filter = ('enabled', 'category')
    search_fields = ('user__username', 'category__name')
