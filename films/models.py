from datetime import datetime
from math import floor

from django.core.validators import MinValueValidator
from django.db import models

from common.constants import CURRENT_YEAR
from common.models import Country, Venue
from directors.models import Director


class Film(models.Model):
    cc_id = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=200)
    spine = models.PositiveIntegerField(null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1870)])
    countries = models.ManyToManyField(Country, related_name="films")
    directors = models.ManyToManyField(Director, related_name="films")
    letterboxd = models.URLField(max_length=200)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def decade(self):
        return 10 * floor(self.year / 10)

    @property
    def current_categories(self):
        return self.categories.filter(year=CURRENT_YEAR)

    @property
    def current_categories_count(self):
        return self.categories.filter(year=CURRENT_YEAR).count()


class FilmSession(models.Model):
    film = models.ForeignKey(Film, related_name="sessions", on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, related_name="sessions", on_delete=models.CASCADE)
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = "Session"
        ordering = ["datetime"]

    def __str__(self):
        return f"{self.datetime.strftime('%d/%m/%Y at %H:%M')}: {self.film}, at {self.venue}"

    @property
    def is_future(self):
        return self.datetime > datetime.now()
