from django import forms
from .models import Election, Position, Candidate, Vote

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'description']

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['bio', 'photo', 'manifesto']

class VoteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election')
        super(VoteForm, self).__init__(*args, **kwargs)
        
        # Dynamically create fields for each position in the election
        for position in election.positions.all():
            candidates = position.candidates.all()
            self.fields[f'position_{position.id}'] = forms.ModelChoiceField(
                queryset=candidates,
                label=position.title,
                widget=forms.RadioSelect,
                required=True
            )
