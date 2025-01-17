from django.core.exceptions import ValidationError
from django.db import models


def validate_year(value):
    if value <= 1880:
        raise ValidationError("Year must be greater than 1800.")


class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[validate_year])
    letterboxd = models.URLField(max_length=200)

    def __str__(self):
        return self.title
