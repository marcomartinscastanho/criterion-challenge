from math import floor

from django.core.validators import MinValueValidator
from django.db import models

from directors.models import Director


class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1870)])
    letterboxd = models.URLField(max_length=200)
    directors = models.ManyToManyField(Director, related_name="films")

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def decade(self):
        return 10 * floor(self.year / 10)
