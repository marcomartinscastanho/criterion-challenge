import json

from django import forms
from django.db.models import Max

from categories.models import Category
from common.constants import CURRENT_YEAR


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)


class CustomJSONField(forms.JSONField):
    empty_values = [None, "", [], ()]


class CategoryForm(forms.ModelForm):
    custom_criteria = CustomJSONField(encoder=PrettyJSONEncoder)

    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["year"].initial = CURRENT_YEAR
            max_number = Category.objects.filter(year=CURRENT_YEAR).aggregate(Max("number"))["number__max"] or 0
            self.fields["number"].initial = max_number + 1
