import csv
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from common.letterboxd import scrape_letterboxd_for_tmdb_id
from films.models import Film
from films.utils import enrich_film_details
from users.forms import ProfileForm
from users.models import UserWatched, UserWatchlist
from users.utils import get_watched_chart_data


@login_required
def profile(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if "csv_file" not in request.FILES:
            if form.is_valid():
                form.save()
                return render(request, "profile.html", {"form": form, "success": "Profile updated successfully!"})
            else:
                return render(request, "profile.html", {"form": form, "error": "The uploaded file must be a CSV file."})
        else:
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                return render(request, "profile.html", {"form": form, "error": "The uploaded file must be a CSV file."})
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
                    return render(request, "profile.html", {"form": form, "success": "Watched films updated!"})
                elif "watchlist" in request.FILES.get("csv_file").name:
                    user_watchlist, _ = UserWatchlist.objects.get_or_create(user=user)
                    user_watchlist.films.set(film_ids)
                    user_watchlist.save()
                    return render(request, "profile.html", {"form": form, "success": "Watchlisted films updated!"})
                return render(request, "profile.html", {"form": form, "error": "Invalid file format."})
            except Exception as e:
                return render(request, "profile.html", {"form": form, "error": f"An error occurred: {e}"})
    form = ProfileForm(instance=user)
    chart_data = get_watched_chart_data(user)
    # in case of a GET
    return render(request, "profile.html", {"form": form, "chart_data": json.dumps(chart_data)})
