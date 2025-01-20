from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpRequest
from django.shortcuts import render

from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR
from users.models import UserWatched, UserWatchlist


@login_required
def categories(request: HttpRequest):
    user = request.user
    user_watched = UserWatched.objects.filter(user=user)
    user_watchlist = UserWatchlist.objects.filter(user=user)
    categories = (
        Category.objects.filter(year=CURRENT_YEAR)
        .annotate(
            films_count=Count("films"),
            watched_count=Subquery(
                user_watched.values("films")
                .filter(films__categories=OuterRef("pk"))
                .annotate(count=Count("films"))
                .values("count")[:1]
            ),
            watchlist_count=Subquery(
                user_watchlist.values("films")
                .filter(films__categories=OuterRef("pk"))
                .annotate(count=Count("films"))
                .values("count")[:1]
            ),
        )
        .values("number", "title", "films_count", "watched_count", "watchlist_count")
    )
    # FIXME: films_count, watched_count and watchlist_count for categories with custom criteria
    return render(request, "categories.html", {"categories": categories})
