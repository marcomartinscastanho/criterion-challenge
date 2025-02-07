import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

from categories.utils import get_category_films
from common.constants import CURRENT_YEAR
from films.models import Film, FilmSession
from picks.models import Pick
from picks.utils import generate_picks
from users.models import User, UserWatched, UserWatchlist


@login_required
def picks(request: HttpRequest):
    user: User = request.user
    # Precompute watched and watchlisted films as sets for quick lookups
    watched_film_ids = UserWatched.objects.filter(user=user).values_list("films__pk", flat=True)
    watchlisted_film_ids = UserWatchlist.objects.filter(user=user).values_list("films__pk", flat=True)
    sessions_soon_film_ids = FilmSession.objects.filter(datetime__gt=now()).values_list("film__pk", flat=True)
    # Fetch all picks for the user in the current year
    picks_qs = Pick.objects.select_related("category", "film").filter(user=user, year=CURRENT_YEAR)
    # Collect all films picked by the user in the current year (for `is_picked` checks)
    picked_film_ids = set(picks_qs.values_list("film__pk", flat=True))
    picks = []
    for pick in picks_qs:
        category = pick.category
        # Use `get_category_films` to calculate eligible films for the category
        all_category_films = get_category_films(category, user)
        films = []
        for film in all_category_films:
            film_id = film.pk
            films.append(
                {
                    "id": film_id,
                    "title": film.title,
                    "year": film.year,
                    "disabled": (film_id in picked_film_ids) or (film_id in watched_film_ids),
                    "watchlisted": film_id in watchlisted_film_ids,
                    "session_soon": film_id in sessions_soon_film_ids,
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
    film_id = data.get("film_id")
    locked = data.get("locked")
    try:
        pick = Pick.objects.get(id=pick_id, user=request.user)
        if film_id:
            pick.film = Film.objects.get(pk=film_id)
        if locked is not None:
            pick.locked = locked
        pick.save()
        return JsonResponse({"success": True})
    except (Pick.DoesNotExist, Film.DoesNotExist):
        return JsonResponse({"success": False, "error": "Pick or Film not found"}, status=404)
