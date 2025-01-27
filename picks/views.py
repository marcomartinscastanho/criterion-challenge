import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

from categories.models import Category
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


@login_required
def suggestions(request: HttpRequest):
    user: User = request.user
    # Precompute user-specific data
    watched_film_ids = UserWatched.objects.filter(user=user).values_list("films__pk", flat=True)
    watchlisted_film_ids = UserWatchlist.objects.filter(user=user).values_list("films__pk", flat=True)
    picked_film_ids = Pick.objects.filter(user=user, year=CURRENT_YEAR).values_list("film__pk", flat=True)
    # Fetch categories for the current year
    locked_category_ids = Pick.objects.filter(user=user, year=CURRENT_YEAR, locked=True).values_list(
        "category__id", flat=True
    )
    categories = Category.objects.filter(year=CURRENT_YEAR).exclude(id__in=locked_category_ids)
    # Prepare data for response
    suggested_changes = []
    for category in categories:
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
                    "film": {"id": session.film.pk, "title": session.film.title, "year": session.film.year},
                    "sessions": [],
                    "watchlisted": session.film.pk in watchlisted_film_ids,
                }
            film_sessions_by_film[session.film.pk]["sessions"].append(
                {"venue": session.venue.name, "datetime": session.datetime}
            )
        # Build alternatives list
        alternatives = [
            {"film": data["film"], "watchlisted": data["watchlisted"], "sessions": data["sessions"]}
            for data in film_sessions_by_film.values()
        ]
        # Skip categories without alternatives
        if not alternatives:
            continue
        # Find the current pick for the category
        picked = Pick.objects.filter(user=user, year=CURRENT_YEAR, category=category).first()
        suggested_changes.append(
            {
                "category_number": category.number,
                "category_title": category.title,
                "pick": {
                    "id": picked.pk if picked else None,
                    "film": {
                        "title": picked.film.title if picked else None,
                        "year": picked.film.year if picked else None,
                    }
                    if picked
                    else None,
                },
                "alternatives": alternatives,
            }
        )

    return render(request, "suggestions.html", {"suggested_changes": suggested_changes})
