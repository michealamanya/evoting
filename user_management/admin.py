from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend the default User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified')
    
    def is_verified(self, obj):
        try:
            return obj.userprofile.is_verified
        except (UserProfile.DoesNotExist, AttributeError):
            return False
    is_verified.boolean = True
    is_verified.short_description = 'Verified'
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to use transaction to ensure user and profile are created together
        """
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"Error saving user: {str(e)}", level='ERROR')
            # Re-raise the error to prevent saving
            raise
    
    def save_formset(self, request, form, formset, change):
        """
        Override save_formset to handle profile creation errors
        """
        try:
            # Check if we're dealing with the profile formset
            if formset.model == UserProfile:
                instances = formset.save(commit=False)
                for instance in instances:
                    # This ensures each profile gets the correctly saved user
                    if not instance.user_id:
                        instance.user = form.instance
                    instance.save()
                formset.save_m2m()
            else:
                formset.save()
        except Exception as e:
            self.message_user(request, f"Error saving profile: {str(e)}", level='ERROR')
            # Re-raise to prevent partial saves
            raise

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
