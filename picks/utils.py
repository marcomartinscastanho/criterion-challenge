from django.db.models import QuerySet

from categories.models import Category
from categories.utils import get_category_films
from common.constants import CURRENT_YEAR
from films.models import Film
from picks.models import Pick
from users.models import User, UserWatched, UserWatchlist


class NoChoicesLeft(Exception):
    pass


def pick_film(watchlisted: QuerySet[Film], all: QuerySet[Film], picked: list[Film]) -> Film:
    for film in watchlisted:
        if film in picked:
            continue
        return film
    for film in all:
        if film in picked:
            continue
        return film
    raise NoChoicesLeft


def generate_picks(user: User):
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    categories_stats = []
    for category in Category.objects.filter(year=CURRENT_YEAR):
        all_category_films = get_category_films(category, user, user_watched_qs, user_watchlist_qs)
        unwatched_films = all_category_films.exclude(pk__in=user_watched_qs).order_by("?")
        watchlisted_films = unwatched_films.filter(pk__in=user_watchlist_qs)
        categories_stats.append(
            {
                "number": category.number,
                "category": category,
                "films": unwatched_films,
                "films_count": len(unwatched_films),
                "watchlisted_films": watchlisted_films,
                "watchlisted_films_count": len(watchlisted_films),
            }
        )
    categories_stats = sorted(
        categories_stats, key=lambda x: (x["watchlisted_films_count"], x["films_count"], x["number"])
    )
    existing_picks = Pick.objects.filter(user=user, year=CURRENT_YEAR)
    picked_films = set(existing_picks.values_list("film", flat=True))
    picked_categories = set(existing_picks.values_list("category", flat=True))
    for category_stats in categories_stats:
        category = category_stats["category"]
        if category in picked_categories:
            continue
        try:
            film = pick_film(category_stats["watchlisted_films"], category_stats["films"], picked_films)
            Pick.objects.create(user=user, year=CURRENT_YEAR, category=category, film=film)
            picked_films.add(film)
        except Exception:
            continue
