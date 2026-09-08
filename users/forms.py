import re
from django import forms
from .models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': '[a-zA-Z ]+',
            'title': 'Letters and spaces only (e.g. John Doe)',
            'placeholder': 'Enter full name (letters and spaces only)'
        }),
        required=True,
        max_length=100
    )
    loginid = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': '(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{5,}',
            'minlength': '5',
            'maxlength': '100',
            'title': 'At least 5 characters containing both letters and numbers (e.g. user101)',
            'placeholder': 'Min 5 characters (letters & numbers, e.g. user101)'
        }),
        required=True,
        max_length=100
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'pattern': '(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,}',
            'title': 'Must contain at least 8 characters, including 1 uppercase letter, 1 lowercase letter, and 1 number',
            'placeholder': 'Min 8 chars: 1 uppercase, 1 lowercase, 1 number'
        }),
        required=True,
        max_length=100
    )
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]{10}',
            'type': 'tel',
            'inputmode': 'numeric',
            'maxlength': '10',
            'minlength': '10',
            'title': 'Must be exactly 10 digits (numbers only)',
            'placeholder': 'Enter 10-digit mobile number (e.g. 9876543210)'
        }),
        required=True,
        max_length=10,
        min_length=10
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$',
            'title': 'Enter a valid email address (e.g. name@example.com)',
            'placeholder': 'e.g. name@example.com'
        }),
        required=True,
        max_length=100
    )
    locality = forms.CharField(
        widget=forms.TextInput(attrs={
            'title': 'Enter your locality or area',
            'placeholder': 'e.g. Landmark, Sector, or Area'
        }),
        required=True,
        max_length=100
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 22,
            'title': 'Enter your complete street address',
            'placeholder': 'Enter complete street address / door number'
        }),
        required=True,
        max_length=250
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'pattern': '[A-Za-z ]+',
            'title': 'Enter characters and spaces only',
            'placeholder': 'e.g. Mumbai, New York (letters only)'
        }),
        required=True,
        max_length=100
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'pattern': '[A-Za-z ]+',
            'title': 'Enter characters and spaces only',
            'placeholder': 'e.g. Maharashtra, California (letters only)'
        }),
        required=True,
        max_length=100
    )
    status = forms.CharField(widget=forms.HiddenInput(), initial='waiting', max_length=100, required=False)

    class Meta():
        model = UserRegistrationModel
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not re.match(r'^[a-zA-Z ]+$', name):
            raise forms.ValidationError('Full name can only contain letters and spaces.')
        return name

    def clean_loginid(self):
        loginid = self.cleaned_data.get('loginid', '').strip()
        if len(loginid) < 5:
            raise forms.ValidationError('Login ID must be at least 5 characters long.')
        if not (any(c.isalpha() for c in loginid) and any(c.isdigit() for c in loginid)):
            raise forms.ValidationError('Login ID must contain both letters and numbers.')
        if not loginid.isalnum():
            raise forms.ValidationError('Login ID can only contain letters and numbers.')
        return loginid

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '').strip()
        if not mobile.isdigit():
            raise forms.ValidationError('Mobile number must contain digits only.')
        if len(mobile) != 10:
            raise forms.ValidationError('Mobile number must be exactly 10 digits.')
        return mobile


