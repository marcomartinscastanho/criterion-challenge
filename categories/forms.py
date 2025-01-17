from django import forms
from django.db.models import Max

from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["year"].initial = CURRENT_YEAR
            max_number = Category.objects.filter(year=CURRENT_YEAR).aggregate(Max("number"))["number__max"] or 0
            self.fields["number"].initial = max_number + 1
