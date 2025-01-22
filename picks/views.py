import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from categories.utils import get_category_films
from criterionchallenge.constants import CURRENT_YEAR
from films.models import Film
from picks.models import Pick
from picks.utils import generate_picks
from users.models import User, UserWatched, UserWatchlist


@login_required
def picks(request: HttpRequest):
    user: User = request.user
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
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
                "id": pick.pk,
                "number": category.number,
                "film": pick.film,
                "locked": pick.locked,
                "category": {"title": category.title, "films": films},
            }
        )

    return render(request, "picks.html", {"picks": picks})


@login_required
def complete_picks(request: HttpRequest):
    user: User = request.user
    Pick.objects.filter(user=user, year=CURRENT_YEAR, locked=False).delete()
    generate_picks(user)
    return redirect("/")


@login_required
@require_http_methods(["PATCH"])
def update_pick(request: HttpRequest, pick_id: int):
    data = json.loads(request.body)
    film_cc_id = data.get("film_cc_id")
    locked = data.get("locked")
    try:
        pick = Pick.objects.get(id=pick_id, user=request.user)
        if film_cc_id:
            pick.film = Film.objects.get(cc_id=film_cc_id)
        if locked is not None:
            pick.locked = locked
        pick.save()
        return JsonResponse({"success": True})
    except (Pick.DoesNotExist, Film.DoesNotExist):
        return JsonResponse({"success": False, "error": "Pick or Film not found"}, status=404)
