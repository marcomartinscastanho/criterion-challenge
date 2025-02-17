from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Index
from django.db.models.functions import ExtractHour, ExtractWeekDay

from common.models import Country, Genre, Keyword, Venue
from directors.models import Director
from films.managers import FilmManager, FilmSessionManager


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
    objects = models.Manager()
    films = FilmManager()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def decade(self):
        return 10 * (self.year // 10)


class FilmSession(models.Model):
    film = models.ForeignKey(Film, related_name="sessions", on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, related_name="sessions", on_delete=models.CASCADE)
    datetime = models.DateTimeField(db_index=True)
    objects = FilmSessionManager()

    class Meta:
        verbose_name = "Session"
        ordering = ["datetime"]
        unique_together = ("film", "venue", "datetime")
        indexes = [
            Index(fields=["datetime"]),
            Index(ExtractHour("datetime"), name="idx_filmsession_hour"),
            Index(ExtractWeekDay("datetime"), name="idx_filmsession_weekday"),
            Index(ExtractWeekDay("datetime"), ExtractHour("datetime"), name="idx_filmsession_day_hour"),
        ]

    def __str__(self):
        return f"{self.datetime.strftime('%d/%m/%Y at %H:%M')}: {self.film}, at {self.venue}"

    @property
    def is_future(self):
        return self.datetime > datetime.now()
