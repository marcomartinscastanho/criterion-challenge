from django import forms

from users.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "date_of_birth"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
        help_texts = {
            "date_of_birth": 'Having your date of birth is important because the pool of available films in some categories depends on your birth year. E.g. "Watch a film from the year you were born"'
        }
