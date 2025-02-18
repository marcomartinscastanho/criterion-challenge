from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import ExpressionWrapper, F, IntegerField, Manager, Max, Min, Q, QuerySet
from django.db.models.functions import ExtractHour, ExtractWeekDay


class FilmQuerySet(QuerySet):
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


class FilmManager(Manager):
    def get_queryset(self) -> FilmQuerySet:
        return FilmQuerySet(self.model, using=self._db)

    def decade_range(self):
        return self.get_queryset().decade_range()


class FilmSessionQuerySet(QuerySet):
    def filter_by_datetime_preference(self, user: AbstractBaseUser) -> QuerySet:
        """
        Filters FilmSession queryset based on user-defined time intervals for each day of the week.
        """
        if not user.preferences or not user.preferences.session_times:
            return self
        queryset = self.annotate(weekday=ExtractWeekDay("datetime"), hour=ExtractHour("datetime"))
        filters = Q()
        for day, interval in user.preferences.session_times.items():
            start = interval["start"]
            end = interval["end"]
            filters |= Q(weekday=day, hour__gte=start, hour__lt=end)
        return queryset.filter(filters)


class FilmSessionManager(Manager):
    def get_queryset(self) -> FilmSessionQuerySet:
        return FilmSessionQuerySet(self.model, using=self._db)

    def filter_by_datetime_preference(self, user: AbstractBaseUser) -> FilmSessionQuerySet:
        return self.get_queryset().filter_by_datetime_preference(user)
