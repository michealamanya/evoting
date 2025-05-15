from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        help_text="Your password can't be too similar to your personal information, must contain at least 8 characters, can't be commonly used, and can't be entirely numeric."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        help_text="Enter the same password as before, for verification."
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly mark required fields
        for field_name in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[field_name].required = True
            if 'class' not in self.fields[field_name].widget.attrs:
                self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        """Validate the entire form data."""
        cleaned_data = super().clean()
        
        # Only check required fields if they haven't already been flagged with errors
        # This prevents contradictory error messages
        required_fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        for field in required_fields:
            if field not in self.errors and (field not in cleaned_data or not cleaned_data.get(field)):
                self.add_error(field, "This field is required.")
        
        # Only check username similarity if password exists and username exists
        username = cleaned_data.get('username', '')
        password = cleaned_data.get('password1', '')
        if username and password and 'password1' not in self.errors:
            if username.lower() in password.lower():
                self.add_error('password1', "The password is too similar to the username.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio', 'date_of_birth', 'phone_number', 'address')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
