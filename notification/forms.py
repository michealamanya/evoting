from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_notifications',
            'election_start_notify',
            'election_end_notify',
            'vote_confirmation_notify',
            'results_notify',
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'election_start_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'election_end_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vote_confirmation_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'results_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
