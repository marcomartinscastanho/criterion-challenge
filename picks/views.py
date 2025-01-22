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
    # if not user.challenge_complete:
    #     pass
    picks = []
    for pick in Pick.objects.select_related("category").filter(user=user).filter(year=CURRENT_YEAR):
        all_category_films = get_category_films(pick.category, user, user_watched_qs, user_watchlist_qs)
        picks.append(
            {
                "film": pick.film,
                "watched": pick.watched,
                "category": {"title": pick.category.title, "films": all_category_films},
            }
        )

    return render(request, "picks.html", {"picks": picks})
