from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now

from categories.models import Category
from categories.utils import get_category_films, len_or_warning
from common.constants import CURRENT_YEAR
from films.models import FilmSession
from picks.models import Pick
from users.models import UserWatched, UserWatchlist


@login_required
def categories(request: HttpRequest):
    user = request.user
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    category_list = []
    for category in Category.objects.filter(year=CURRENT_YEAR).order_by("number"):
        films = get_category_films(category, user)
        user_watched_films = films.filter(pk__in=user_watched_qs)
        user_watchlist_films = films.filter(pk__in=user_watchlist_qs)
        # user pick
        try:
            pick = Pick.objects.get(user=user, category=category)
            pick_film = pick.film
            is_locked = pick.locked
            is_watched = pick.film in user_watched_films
            is_watchlisted = pick.film in user_watchlist_films
            has_session = (
                FilmSession.objects.filter_by_datetime_preference(user)
                .filter(film=pick.film, datetime__gt=now())
                .exists()
            )
            pick = {
                "film": str(pick_film),
                "locked": is_locked,
                "watched": is_watched,
                "watchlisted": is_watchlisted,
                "session": has_session,
            }
        except Pick.DoesNotExist:
            pick = None
        category_list.append(
            {
                "id": category.pk,
                "number": category.number,
                "title": category.title,
                "films_count": len_or_warning(films),
                "watched_count": len(user_watched_films),
                "watchlist_count": len(user_watchlist_films),
                "pick": pick,
            }
        )
    # Sorting logic
    sort_param = request.GET.get("sort", "number")
    reverse = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")
    valid_sort_keys = {"number", "films_count", "watched_count", "watchlist_count"}
    if sort_key in valid_sort_keys:
        category_list.sort(key=lambda x: x[sort_key], reverse=reverse)
    return render(request, "categories.html", {"categories": category_list})


@login_required
def category_detail(request: HttpRequest, category_id: int):
    user = request.user
    category = get_object_or_404(Category, id=category_id)
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    films = get_category_films(category, user)
    pick = Pick.objects.filter(user=user, category=category).first()
    user_picks = Pick.objects.filter(user=user, year=CURRENT_YEAR).values("film")
    film_objects = [
        {
            "id": film.pk,
            "title": film.title,
            "year": film.year,
            "directors": ", ".join(map(str, film.directors.all())),
            "url": film.letterboxd,
            "watched": user_watched_qs.filter(films=film).exists(),
            "watchlisted": user_watchlist_qs.filter(films=film).exists(),
            "is_pick": pick is not None and film.pk == pick.film.pk,
            "picked": user_picks.filter(film=film).exists(),
            "sessions": [
                {"venue": session.venue, "date": session.datetime}
                for session in FilmSession.objects.filter(film=film, datetime__gt=now())
            ],
        }
        for film in films
    ]
    response = {
        "category": {
            "id": category.pk,
            "number": category.number,
            "title": category.title,
            "films": film_objects,
            "locked": pick.locked if pick else False,
        }
    }
    return render(request, "category.html", response)
