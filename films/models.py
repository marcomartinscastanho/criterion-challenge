from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models

from common.models import Country, Genre, Keyword, Venue
from directors.models import Director

# TODO: custom queryset that creates filters for QuerySet[Film] such as:
# https://stackoverflow.com/a/29798508/1971089
#   - has_tmdb_data = has directors and has country and has genres and has runtime
#   - has_letterboxd = has letterboxd url
#   - is_ready = has_tmdb_data and has_letterboxd
#   - is_criterion = has cc_id
#   - is_feature = runtime >= 40


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
        return self.title

    # TODO: on save(), if not self.tmdb_id -> get tmdb data


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
