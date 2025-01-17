from django import forms

from categories.constants import CURRENT_YEAR
from categories.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["year"].initial = CURRENT_YEAR
