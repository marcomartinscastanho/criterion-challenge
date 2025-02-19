import csv
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from common.letterboxd import scrape_letterboxd_for_tmdb_id
from films.models import Film
from films.utils import enrich_film_details
from users.forms import PickOrderCriteriaForm, ProfileForm, SessionTimesForm
from users.models import UserPreference, UserWatched, UserWatchlist
from users.utils import get_days_of_week, get_watched_chart_data


@login_required
def profile(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(
                request, "user/profile/profile.html", {"form": form, "success": "Profile updated successfully!"}
            )
    form = ProfileForm(instance=user)
    # in case of a GET
    return render(request, "user/profile/profile.html", {"form": form})


@login_required
def film_stats(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith(".csv"):
            return render(request, "user/stats/stats.html", {"error": "The uploaded file must be a CSV file."})
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            film_ids = []
            for row in reader:
                title = row["Name"]
                year = row["Year"]
                uri = row["Letterboxd URI"]
                if not all([title, year, uri]):
                    continue
                try:
                    film = Film.objects.get(letterboxd=uri)
                except Film.DoesNotExist:
                    tmdb_id = scrape_letterboxd_for_tmdb_id(uri)
                    if not tmdb_id:
                        print(f"Skipping {title} ({year}) - tmdb_id not found in letterboxd page")
                        continue
                    film = Film.objects.create(title=title, year=year, letterboxd=uri, tmdb_id=tmdb_id)
                    enrich_film_details(film)
                film_ids.append(film.pk)
            if "watched" in request.FILES.get("csv_file").name:
                user_watched, _ = UserWatched.objects.get_or_create(user=user)
                user_watched.films.set(film_ids)
                user_watched.save()
                return render(request, "user/stats/stats.html", {"success": "Watched films updated!"})
            elif "watchlist" in request.FILES.get("csv_file").name:
                user_watchlist, _ = UserWatchlist.objects.get_or_create(user=user)
                user_watchlist.films.set(film_ids)
                user_watchlist.save()
                return render(request, "user/stats/stats.html", {"success": "Watchlisted films updated!"})
            return render(request, "user/stats/stats.html", {"error": "Invalid file format."})
        except Exception as e:
            return render(request, "user/stats/stats.html", {"error": f"An error occurred: {e}"})
    else:
        # GET
        chart_data = get_watched_chart_data(user)
        return render(request, "user/stats/stats.html", {"chart_data": json.dumps(chart_data)})


@login_required
def preferences(request):
    user_prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    pick_order_form = PickOrderCriteriaForm(instance=user_prefs)
    session_times_form = SessionTimesForm(instance=user_prefs)
    return render(
        request,
        "user/preferences/preferences.html",
        {
            "pick_order_form": pick_order_form,
            "session_times_form": session_times_form,
            "days_of_week": get_days_of_week(),
        },
    )


@login_required
def update_pick_order_criteria(request):
    user_prefs = request.user.preferences
    if request.method == "POST":
        form = PickOrderCriteriaForm(request.POST, instance=user_prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Pick order criteria updated successfully.")
    return redirect("preferences")


@login_required
def update_session_times(request):
    user_prefs = request.user.preferences
    # unchecked chatgpt code...
    if request.method == "POST":
        session_times_data = {}
        for key, value in request.POST.items():
            if key.startswith("session_times"):
                parts = key.split("[")
                day_num = parts[1][:-1]  # Extract day number
                field = parts[2][:-1]  # Extract field (start/end)
                if day_num not in session_times_data:
                    session_times_data[day_num] = {}
                session_times_data[day_num][field] = int(value)
        user_prefs.session_times = session_times_data
        user_prefs.save()
        messages.success(request, "Session times updated successfully.")
    return redirect("preferences")


# FIXME: give this a better name
@login_required
@require_http_methods(["PATCH"])
def update_filter_preferences(request: HttpRequest):
    user = request.user
    data = json.loads(request.body)
    filter_not_watched = data.get("filter_not_watched")
    filter_watchlisted = data.get("filter_watchlisted")
    filter_with_sessions = data.get("filter_with_sessions")
    UserPreference.objects.get_or_create(user=user)
    if filter_not_watched is not None:
        UserPreference.objects.filter(user=user).update(filter_not_watched=filter_not_watched)
    if filter_watchlisted is not None:
        UserPreference.objects.filter(user=user).update(filter_watchlisted=filter_watchlisted)
    if filter_with_sessions is not None:
        UserPreference.objects.filter(user=user).update(filter_with_sessions=filter_with_sessions)
    return JsonResponse({"success": True})
