from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from categories.utils import get_category_alternatives, get_category_films, len_or_warning
from common.constants import CURRENT_YEAR
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
        category_list.append(
            {
                "id": category.pk,
                "number": category.number,
                "title": category.title,
                "films_count": len_or_warning(films),
                "watched_count": len(user_watched_films),
                "watchlist_count": len(user_watchlist_films),
            }
        )
    return render(request, "categories.html", {"categories": category_list})


@login_required
def category_detail(request: HttpRequest, category_id: int):
    user = request.user
    category = get_object_or_404(Category, id=category_id)
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    films = get_category_films(category, user)
    pick = Pick.objects.filter(user=user, category=category).first()
    film_objects = [
        {
            "title": film.title,
            "year": film.year,
            "url": film.letterboxd,
            "watched": user_watched_qs.filter(films=film).exists(),
            "watchlisted": user_watchlist_qs.filter(films=film).exists(),
        }
        for film in films
    ]
    response = {"category": {"number": category.number, "title": category.title, "films": film_objects}}
    if pick:
        response["pick"] = {
            "id": pick.pk,
            "film": str(pick.film),
            "url": pick.film.letterboxd,
            "is_locked": pick.locked,
            "watchlisted": user_watchlist_qs.filter(films=pick.film).exists(),
        }
    alternatives = get_category_alternatives(category=category, user=user)
    if alternatives:
        response["alternatives"] = alternatives
    return render(request, "category.html", response)
