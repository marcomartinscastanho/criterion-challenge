from django.db.models import Q, QuerySet
from django.utils.timezone import now

from categories.models import Category
from common.constants import CURRENT_YEAR
from films.models import Film, FilmSession
from films.utils import filter_films_by_criteria
from picks.models import Pick
from users.models import User, UserWatched, UserWatchlist


def get_category_films(category: Category, user: User):
    if category.films.exists():
        return category.films.all()
    if not category.custom_criteria:
        return Film.objects.none()
    films = Film.objects.all()
    return filter_films_by_criteria(films, category.custom_criteria, user)


def len_or_warning(qs: QuerySet):
    return len(qs) if qs.exists() else "⚠️"


def get_category_alternatives(category: Category, user: User):
    # Precompute user-specific data
    watched_film_ids = UserWatched.objects.filter(user=user).values_list("films__pk", flat=True)
    watchlisted_film_ids = UserWatchlist.objects.filter(user=user).values_list("films__pk", flat=True)
    picked_film_ids = Pick.objects.filter(user=user, year=CURRENT_YEAR).values_list("film__pk", flat=True)
    # Get films eligible for the category
    category_films = get_category_films(category, user)
    # Filter out films already picked or watched
    eligible_films = category_films.exclude(Q(pk__in=watched_film_ids) | Q(pk__in=picked_film_ids))
    # Fetch future sessions for eligible films
    film_sessions = (
        FilmSession.objects.filter(film__in=eligible_films, datetime__gt=now())
        .select_related("venue", "film")
        .order_by("datetime")
    )
    # Group sessions by film
    film_sessions_by_film = {}
    for session in film_sessions:
        if session.film.pk not in film_sessions_by_film:
            film_sessions_by_film[session.film.pk] = {
                "film": {
                    "id": session.film.pk,
                    "title": session.film.title,
                    "year": session.film.year,
                    "url": session.film.letterboxd,
                },
                "sessions": [],
                "watchlisted": session.film.pk in watchlisted_film_ids,
            }
        film_sessions_by_film[session.film.pk]["sessions"].append(
            {"venue": session.venue.name, "datetime": session.datetime}
        )
    # sessions list
    return [
        {"film": data["film"], "watchlisted": data["watchlisted"], "sessions": data["sessions"]}
        for data in film_sessions_by_film.values()
    ]
