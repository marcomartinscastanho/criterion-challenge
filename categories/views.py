from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from criterionchallenge.constants import CURRENT_YEAR
from directors.models import Director
from films.models import Film
from users.models import User, UserWatched, UserWatchlist


def get_category_films(
    category: Category,
    user: User,
    user_watched_qs: QuerySet[UserWatched],
    user_watchlist_qs: QuerySet[UserWatchlist],
):
    if category.films.exists():
        films = category.films.all()
    elif category.custom_criteria:
        films = Film.objects.all()
        for key, value in category.custom_criteria.items():
            if key == "year" and value == "user__date_of_birth":
                if not user.date_of_birth:
                    return Film.objects.none(), Film.objects.none(), Film.objects.none()
                films = films.filter(year=user.date_of_birth.year)
            if key == "spine" and value == "not_null":
                films = films.filter(spine__isnull=False)
            if key == "in" and value == "user__watchlist":
                if not user_watchlist_qs:
                    return Film.objects.none(), Film.objects.none(), Film.objects.none()
                films = films.filter(pk__in=user_watchlist_qs.values_list("films", flat=True))
            if key == "director":
                for key2, value2 in value.items():
                    if key2 == "not_in" and value2 == "user__films":
                        if not user_watched_qs:
                            return Film.objects.none(), Film.objects.none(), Film.objects.none()
                        watched_directors = Director.objects.filter(
                            films__in=user_watched_qs.values_list("films", flat=True)
                        ).distinct()
                        films = films.exclude(directors__in=watched_directors)
    return films


def len_or_warning(qs: QuerySet):
    return len(qs) if qs.exists() else "⚠️"


@login_required
def categories(request: HttpRequest):
    user = request.user
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    category_list = []
    for category in Category.objects.filter(year=CURRENT_YEAR).order_by("number"):
        films = get_category_films(category, user, user_watched_qs, user_watchlist_qs)
        user_watched_films = films.filter(pk__in=user_watched_qs)
        user_watchlist_films = films.filter(pk__in=user_watchlist_qs)
        category_list.append(
            {
                "id": category.pk,
                "number": category.number,
                "title": category.title,
                "films_count": len_or_warning(films),
                "watched_count": len(user_watched_films),
                "watchlist_count": len(user_watchlist_films),
            }
        )
    return render(request, "categories.html", {"categories": category_list})


@login_required
def category_detail(request, category_id):
    user = request.user
    category = get_object_or_404(Category, id=category_id)
    user_watched_qs = UserWatched.objects.filter(user=user).values("films")
    user_watchlist_qs = UserWatchlist.objects.filter(user=user).values("films")
    films = get_category_films(category, user, user_watched_qs, user_watchlist_qs)
    film_objects = [
        {
            "title": film.title,
            "year": film.year,
            "url": film.letterboxd,
            "watched": user_watched_qs.filter(films=film).exists(),
            "watchlisted": user_watchlist_qs.filter(films=film).exists(),
        }
        for film in films
    ]
    return render(
        request,
        "category.html",
        {"category": {"number": category.number, "title": category.title, "films": film_objects}},
    )
