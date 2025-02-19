from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class RegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        help_text="Your birth year is needed ofr categories such as 'Watch a movie from the year you were born'.",
    )

    class Meta:
        model = User
        fields = ["username", "date_of_birth", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"type": "password", "class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"type": "password", "class": "form-control"}),
        }
        help_texts = {
            "username": "Your Letterboxd username.",
        }
