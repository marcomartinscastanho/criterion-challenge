from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ExpressionWrapper, F, IntegerField, Max, Min

from common.models import Country, Genre, Keyword, Venue
from directors.models import Director


class FilmQuerySet(models.QuerySet):
    def is_feature(self):
        """Filters only feature films (runtime >= 40 minutes)."""
        return self.filter(runtime__gte=40)

    def with_decade(self):
        """Annotates each film with its decade."""
        return self.annotate(decade=ExpressionWrapper(F("year") / 10 * 10, output_field=IntegerField()))

    def filter_by_decade(self, decade):
        """Filters films belonging to a specific decade."""
        return self.filter(year__gte=decade, year__lt=decade + 10)

    def decade_range(self) -> tuple[int | None, int | None]:
        """Returns the start and end decades dynamically."""
        feature_films = self.is_feature()
        min_year = feature_films.aggregate(Min("year"))["year__min"]
        max_year = feature_films.aggregate(Max("year"))["year__max"]
        if min_year and max_year:
            start_decade = (min_year // 10) * 10
            end_decade = (max_year // 10) * 10
            return start_decade, end_decade
        return None, None


class FilmManager(models.Manager):
    def get_queryset(self) -> FilmQuerySet:
        return FilmQuerySet(self.model, using=self._db)

    def decade_range(self):
        return self.get_queryset().decade_range()


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
