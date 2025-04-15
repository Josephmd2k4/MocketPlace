from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
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
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',  # Make email read-only
            'style': 'background-color:#f1f1f1;'  # Optional: gray it out
        }),
        required=False  # Not required for submission anymore
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_email(self):
        # Always return initial email; don't allow changes
        return self.initial.get('email')

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    email = forms.EmailField(required=True, help_text="Must be an flsouthern.edu email.")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.lower().endswith('@flsouthern.edu'):
            raise forms.ValidationError("Email must be a flsouthern.edu address.")
        return email

User = get_user_model()

class CustomUserChangeForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color:#f1f1f1;'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
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

    def clean_email(self):
        return self.initial.get('email')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].label = 'Confirm New Password'
        self.fields['new_password2'].help_text = ''
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
