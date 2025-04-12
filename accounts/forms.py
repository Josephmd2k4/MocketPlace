from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        required=True
    )
    profile_image = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'bio', 'year_in_school', 'major', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'year_in_school': forms.Select(choices=[
                ('Freshman', 'Freshman'),
                ('Sophomore', 'Sophomore'),
                ('Junior', 'Junior'),
                ('Senior', 'Senior'),
                ('Graduate', 'Graduate')
            ], attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your major...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user object
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

User = get_user_model()

class CustomUserChangeForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself...'}), 
        required=False
    )
    year_in_school = forms.ChoiceField(
        choices=[
            ('Freshman', 'Freshman'),
            ('Sophomore', 'Sophomore'),
            ('Junior', 'Junior'),
            ('Senior', 'Senior'),
            ('Graduate', 'Graduate')
        ], 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=False
    )
    major = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your major...'}), 
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'year_in_school', 'major', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].label = 'Confirm New Password'  # Customize the label
        self.fields['new_password2'].help_text = ''  # Remove the help text
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
