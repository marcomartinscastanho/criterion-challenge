from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from categories.utils import get_category_films
from criterionchallenge.constants import CURRENT_YEAR
from picks.models import Pick
from users.models import User, UserWatched, UserWatchlist


@login_required
def picks(request: HttpRequest):
    user: User = request.user
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    if not user.challenge_complete:
        pass  # TODO
    picks = []
    picks_qs = Pick.objects.select_related("category").filter(user=user).filter(year=CURRENT_YEAR)
    for pick in picks_qs:
        all_category_films = get_category_films(pick.category, user, user_watched_qs, user_watchlist_qs)
        category = pick.category
        films = []
        other_picks = picks_qs.exclude(pk=pick.pk)
        for film in all_category_films:
            is_picked = other_picks.values("film").filter(film=film).exists()
            is_watched = user_watched_qs.filter(films=film).exists()
            is_watchlisted = user_watchlist_qs.filter(films=film).exists()
            films.append(
                {
                    "cc_id": film.cc_id,
                    "title": film.title,
                    "year": film.year,
                    "disabled": is_picked or is_watched,
                    "watchlisted": is_watchlisted,
                }
            )
        picks.append(
            {
                "number": category.number,
                "film": pick.film,
                "watched": pick.watched,
                "category": {"title": category.title, "films": films},
            }
        )

    return render(request, "picks.html", {"picks": picks})
