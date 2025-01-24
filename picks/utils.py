from django.db.models import Count, Q

from categories.models import Category
from categories.utils import get_category_films
from common.constants import CURRENT_YEAR
from picks.models import Pick
from users.models import User, UserWatched, UserWatchlist


class NoChoicesLeft(Exception):
    pass


def generate_picks(user: User):
    user_watched_ids = UserWatched.objects.filter(user=user).values_list("films__pk", flat=True)
    user_watchlist_ids = UserWatchlist.objects.filter(user=user).values_list("films__pk", flat=True)
    # Fetch existing picks to avoid duplicates
    existing_picks = Pick.objects.filter(user=user, year=CURRENT_YEAR)
    picked_film_ids = set(existing_picks.values_list("film__pk", flat=True))
    picked_category_ids = set(existing_picks.values_list("category__pk", flat=True))
    # Fetch all categories for the current year
    categories = Category.objects.filter(year=CURRENT_YEAR)
    # Iterate through categories and create picks
    for category in categories:
        if category.id in picked_category_ids:
            continue
        # Get eligible films for the category
        all_category_films = get_category_films(
            category=category,
            user=user,
            user_watched_qs=user_watched_ids,
            user_watchlist_qs=user_watchlist_ids,
        )
        # Randomize and prioritize watchlisted films
        all_category_films = (
            all_category_films.exclude(pk__in=user_watched_ids)
            .annotate(is_watchlisted=Count("pk", filter=Q(pk__in=user_watchlist_ids)))
            .order_by("-is_watchlisted", "?")
        )
        film = next((film for film in all_category_films if film.pk not in picked_film_ids), None)
        if film:
            Pick.objects.create(user=user, year=CURRENT_YEAR, category=category, film=film)
            picked_film_ids.add(film.pk)
