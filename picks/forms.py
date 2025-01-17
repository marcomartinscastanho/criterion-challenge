from django import forms

from criterionchallenge.constants import CURRENT_YEAR
from picks.models import Pick


class PickForm(forms.ModelForm):
    class Meta:
        model = Pick
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["year"].initial = CURRENT_YEAR
