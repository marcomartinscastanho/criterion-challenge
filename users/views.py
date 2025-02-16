import csv
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from common.letterboxd import scrape_letterboxd_for_tmdb_id
from films.models import Film
from films.utils import enrich_film_details
from users.forms import ProfileForm
from users.models import UserPreference, UserWatched, UserWatchlist
from users.utils import get_watched_chart_data


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
        else:
            return render(
                request, "user/profile/profile.html", {"form": form, "error": "The uploaded file must be a CSV file."}
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
@require_http_methods(["PATCH"])
def set_pick_order_criteria(request: HttpRequest):
    user = request.user
    data = json.loads(request.body)
    criteria = data.get("criteria")
    preferences, _ = UserPreference.objects.get_or_create(user=user)
    preferences.pick_order_criteria = criteria
    preferences.save()
    return JsonResponse({"success": True})


@login_required
@require_http_methods(["PATCH"])
def update_time_preferences(request: HttpRequest):
    user = request.user
    try:
        data = json.loads(request.body)
        user_prefs, _ = UserPreference.objects.get_or_create(user=user)
        user_prefs.session_times = data
        user_prefs.save()
        return JsonResponse({"success": True, "message": "Preferences updated successfully!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
def preferences(request: HttpRequest):
    days_of_week = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    return render(request, "user/preferences/preferences.html", {"days_of_week": days_of_week})
