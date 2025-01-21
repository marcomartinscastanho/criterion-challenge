from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.http import HttpRequest
from django.shortcuts import render

from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR
from directors.models import Director
from films.models import Film
from users.models import User, UserWatched, UserWatchlist


def parse_custom_criteria(criteria: dict, user: User):
    films = Film.objects.all()
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    for key, value in criteria.items():
        if key == "year" and value == "user__date_of_birth":
            if not user.date_of_birth:
                return "⚠️", "⚠️", "⚠️"
            films = films.filter(year=user.date_of_birth.year)
        if key == "spine" and value == "not_null":
            films = films.filter(spine__isnull=False)
        if key == "in" and value == "user__watchlist":
            if not user_watchlist_qs:
                return "⚠️", "⚠️", "⚠️"
            films = films.filter(pk__in=user_watchlist_qs.values_list("films", flat=True))
        if key == "director":
            for key2, value2 in value.items():
                if key2 == "not_in" and value2 == "user__films":
                    if not user_watched_qs:
                        return "⚠️", "⚠️", "⚠️"
                    watched_directors = Director.objects.filter(
                        films__in=user_watched_qs.values_list("films", flat=True)
                    ).distinct()
                    films = films.exclude(directors__in=watched_directors)
    user_watched_films = user_watched_qs.filter(films__in=films).distinct()
    user_watchlist_films = user_watchlist_qs.filter(films__in=films).distinct()
    return films.count(), user_watched_films.count(), user_watchlist_films.count()


@login_required
def categories(request: HttpRequest):
    user = request.user
    user_watched_qs = UserWatched.objects.filter(user=user)
    user_watchlist_qs = UserWatchlist.objects.filter(user=user)
    categories = (
        Category.objects.prefetch_related(
            Prefetch("films"),
            Prefetch("films__userwatched_set", queryset=user_watched_qs, to_attr="watched_for_user"),
            Prefetch("films__userwatchlist_set", queryset=user_watchlist_qs, to_attr="watchlist_for_user"),
        )
        .filter(year=CURRENT_YEAR)
        .annotate(films_count=Count("films", distinct=True))
        .order_by("number")
    )
    category_list = []
    for category in categories:
        if category.films.exists():
            films_count = category.films.count()
            watched_count = sum(1 for film in category.films.all() if film.watched_for_user)
            watchlist_count = sum(1 for film in category.films.all() if film.watchlist_for_user)
        elif category.custom_criteria:
            films_count, watched_count, watchlist_count = parse_custom_criteria(category.custom_criteria, user)
        else:
            films_count = 0
            watched_count = 0
            watchlist_count = 0
        category_list.append(
            {
                "number": category.number,
                "title": category.title,
                "films_count": films_count,
                "watched_count": watched_count,
                "watchlist_count": watchlist_count,
            }
        )
    return render(request, "categories.html", {"categories": category_list})
