from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models

from common.models import Country, Genre, Keyword, Venue
from directors.models import Director


class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1870)])
    directors = models.ManyToManyField(Director, related_name="films")
    countries = models.ManyToManyField(Country, related_name="films")
    genres = models.ManyToManyField(Genre, related_name="films", blank=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    keywords = models.ManyToManyField(Keyword, related_name="films", blank=True)
    letterboxd = models.URLField(max_length=200)
    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    cc_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    spine = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.year})"


class FilmSession(models.Model):
    film = models.ForeignKey(Film, related_name="sessions", on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, related_name="sessions", on_delete=models.CASCADE)
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = "Session"
        ordering = ["datetime"]
        unique_together = ("film", "venue", "datetime")

    def __str__(self):
        return f"{self.datetime.strftime('%d/%m/%Y at %H:%M')}: {self.film}, at {self.venue}"

    @property
    def is_future(self):
        return self.datetime > datetime.now()
