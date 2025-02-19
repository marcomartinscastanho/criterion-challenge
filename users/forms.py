from django import forms

from users.models import User, UserPreference


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
        help_text='Having your date of birth is important because the pool of available films in some categories depends on your birth year. E.g. "Watch a film from the year you were born"',
    )

    class Meta:
        model = User
        fields = ["username", "date_of_birth"]
        widgets = {"username": forms.TextInput(attrs={"class": "form-control"})}
        help_texts = {"username": "Should match your Letterboxd username."}


class PickOrderCriteriaForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ["pick_order_criteria"]
        widgets = {"pick_order_criteria": forms.HiddenInput()}


class SessionTimesForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ["session_times"]
        widgets = {"session_times": forms.HiddenInput()}
