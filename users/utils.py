from django.db.models import Count, ExpressionWrapper, F, IntegerField

from common.letterboxd import scrape_letterboxd_list_page
from films.models import Film
from users.constants import WATCHED_URL, WATCHLIST_URL
from users.models import User, UserWatched, UserWatchlist


def get_watched_chart_data(user: User):
    start_decade, end_decade = Film.films.filter(runtime__gte=40).decade_range()
    decades = [str(year) for year in range(start_decade, end_decade + 1, 10)]
    try:
        # Annotate watched and watchlisted films with decades
        watched_films = (
            UserWatched.objects.get(user=user)
            .films.filter(runtime__gte=40)
            .annotate(decade=ExpressionWrapper((F("year") / 10) * 10, output_field=IntegerField()))
            .values("decade")
            .annotate(count=Count("id"))
        )
        watchlisted_films = (
            UserWatchlist.objects.get(user=user)
            .films.filter(runtime__gte=40)
            .annotate(decade=ExpressionWrapper((F("year") / 10) * 10, output_field=IntegerField()))
            .values("decade")
            .annotate(count=Count("id"))
        )
        # Convert querysets to decade-based dictionaries
        watched_count = {entry["decade"]: entry["count"] for entry in watched_films}
        watchlisted_count = {entry["decade"]: entry["count"] for entry in watchlisted_films}
        # Prepare data arrays
        bar_data_1 = []  # Watched films per decade
        bar_data_2 = []  # Watchlisted films per decade
        line_data = []  # Percentage watched (watched / (watched + watchlisted))
        for decade in map(int, decades):
            watched = watched_count.get(decade, 0)
            watchlisted = watchlisted_count.get(decade, 0)
            total = watched + watchlisted
            bar_data_1.append(watched)
            bar_data_2.append(watchlisted)
            line_data.append(round(watched / total * 100, 1) if total > 0 else 0)  # Avoid division by zero
        return {"decades": decades, "bar_data_1": bar_data_1, "bar_data_2": bar_data_2, "line_data": line_data}
    except (UserWatched.DoesNotExist, UserWatchlist.DoesNotExist):
        return {}


def get_days_of_week():
    return {
        "1": "Sunday",
        "2": "Monday",
        "3": "Tuesday",
        "4": "Wednesday",
        "5": "Thursday",
        "6": "Friday",
        "7": "Saturday",
    }


def get_user_watched_films(user: User):
    film_ids = []
    page = 1
    while True:
        url = WATCHED_URL.format(username=user.username, page=page)
        films = scrape_letterboxd_list_page(url)
        if films is None:
            break
        film_ids.extend(films)
        page += 1
    user_watched, _ = UserWatched.objects.get_or_create(user=user)
    user_watched.films.set(film_ids)
    user_watched.save()


def get_user_watchlist_films(user: User):
    film_ids = []
    page = 1
    while True:
        url = WATCHLIST_URL.format(username=user.username, page=page)
        films = scrape_letterboxd_list_page(url)
        if films is None:
            break
        film_ids.extend(films)
        page += 1
    user_watchlist, _ = UserWatchlist.objects.get_or_create(user=user)
    user_watchlist.films.set(film_ids)
    user_watchlist.save()
