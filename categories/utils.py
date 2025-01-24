from django.db.models import QuerySet

from categories.models import Category
from directors.models import Director
from films.models import Film
from users.models import User, UserWatched, UserWatchlist


def get_category_films(
    category: Category,
    user: User,
    user_watched_qs: QuerySet[UserWatched],
    user_watchlist_qs: QuerySet[UserWatchlist],
):
    if category.films.exists():
        return category.films.all()

    if not category.custom_criteria:
        return Film.objects.none()

    films = Film.objects.all()
    for key, value in category.custom_criteria.items():
        if key == "year" and value == "user__date_of_birth":
            if not user.date_of_birth:
                return Film.objects.none()
            films = films.filter(year=user.date_of_birth.year)
        if key == "spine" and value == "not_null":
            films = films.filter(spine__isnull=False)
        if key == "in" and value == "user__watchlist":
            watchlist_ids = user_watchlist_qs.values_list("films__pk", flat=True)
            if not watchlist_ids.exists():
                return Film.objects.none()
            films = films.filter(pk__in=watchlist_ids)
        if key == "director":
            for key2, value2 in value.items():
                if key2 == "not_in" and value2 == "user__films":
                    if not user_watched_qs:
                        return Film.objects.none()
                    watched_directors = Director.objects.filter(
                        films__in=user_watched_qs.values_list("films", flat=True)
                    ).distinct()
                    films = films.exclude(directors__in=watched_directors)
    return films


def len_or_warning(qs: QuerySet):
    return len(qs) if qs.exists() else "⚠️"
