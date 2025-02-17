from django.db.models import BooleanField, Case, Exists, IntegerField, OuterRef, QuerySet, Value, When
from django.utils.timezone import now

from categories.models import Category
from categories.utils import get_category_films
from common.constants import CURRENT_YEAR
from films.models import Film, FilmSession
from picks.models import Pick
from users.models import User, UserWatched, UserWatchlist
from users.utils import get_watched_chart_data


class DecadeWeights:
    def __init__(self, user: User):
        chart_data = get_watched_chart_data(user)
        self.decade_map = {
            int(decade): {
                "watched": chart_data["bar_data_1"][i],
                "watchlisted": chart_data["bar_data_2"][i],
                "percentage": DecadeWeights._calc_percentage(chart_data["bar_data_1"][i], chart_data["bar_data_2"][i]),
            }
            for i, decade in enumerate(chart_data["decades"])
        }
        # add locked picks not yet watched to the decade weights
        user_watched_ids = UserWatched.objects.filter(user=user).values_list("films__pk", flat=True)
        locked_picks = Pick.objects.filter(user=user, year=CURRENT_YEAR, locked=True)
        for locked_pick in locked_picks:
            if locked_pick.film.pk not in user_watched_ids:
                self.add_to_decade(locked_pick.film.decade)

    @staticmethod
    def _calc_percentage(watched: int, watchlisted: int):
        total = watched + watchlisted
        return round(watched / total * 100, 1) if total > 0 else 0

    def cases(self):
        decade_percentage_map = {decade: data["percentage"] for decade, data in self.decade_map.items()}
        cases = [
            When(year__gte=decade, year__lt=decade + 10, then=percentage)
            for decade, percentage in decade_percentage_map.items()
        ]
        return cases

    def add_to_decade(self, decade: int):
        decade_data = self.decade_map[decade]
        decade_data["watched"] += 1
        decade_data["percentage"] = DecadeWeights._calc_percentage(decade_data["watched"], decade_data["watchlisted"])
        self.decade_map[decade] = decade_data


def _sort_categories(categories: list[Category], category_films_map: dict[int, QuerySet[Film]]):
    # Compute number of films per category
    category_film_counts = {category_id: films.count() for category_id, films in category_films_map.items()}
    # Sort categories by film count (descending for more films first)
    sorted_categories = sorted(categories, key=lambda c: category_film_counts.get(c.pk, 0))
    # Define ordering with Case
    order_cases = [When(pk=category.pk, then=pos) for pos, category in enumerate(sorted_categories)]
    # Annotate and order categories by those with fewer films
    categories = (
        Category.objects.filter(pk__in=category_film_counts.keys())
        .annotate(sort_order=Case(*order_cases, output_field=IntegerField()))
        .order_by("sort_order")
    )
    return categories


def _get_order_by(user: User):
    try:
        order_by_criteria: list[str] = user.preferences.pick_order_criteria
    except Exception:
        order_by_criteria: list[str] = []
    return order_by_criteria + ["?"]


def generate_picks(user: User):
    user_watched_ids = set(UserWatched.objects.filter(user=user).values_list("films__pk", flat=True))
    # Fetch existing picks to avoid duplicates
    existing_picks = Pick.objects.filter(user=user, year=CURRENT_YEAR)
    picked_film_ids = set(existing_picks.values_list("film__pk", flat=True))
    picked_category_ids = set(existing_picks.values_list("category__pk", flat=True))
    # Fetch all categories for the current year
    categories = list(Category.objects.filter(year=CURRENT_YEAR))
    # Get films for each category
    category_films_map = {category.pk: get_category_films(category=category, user=user) for category in categories}
    # Sort categories by those with fewer films first
    categories = _sort_categories(categories, category_films_map)
    # Initializer decade weights
    decade_weights = DecadeWeights(user)
    # Set default order criteria
    order_by_criteria = _get_order_by(user)
    # Iterate through categories and create picks
    for category in categories:
        # Skip categories already picked
        if category.pk in picked_category_ids:
            continue
        # Get eligible films for this category
        all_category_films = category_films_map[category.pk]
        # Randomize and then prioritize watchlisted films
        all_category_films = (
            all_category_films.exclude(pk__in=user_watched_ids)
            .annotate(is_watchlisted=Exists(UserWatchlist.objects.filter(user=user, films=OuterRef("pk"))))
            .annotate(
                decade_watched_percentage=Case(*(decade_weights.cases()), default=100, output_field=IntegerField())
            )
            .annotate(
                has_future_session=Exists(
                    FilmSession.objects.filter_by_datetime_preference(user).filter(
                        film=OuterRef("pk"), datetime__gt=now()
                    )
                )
            )
            .annotate(
                has_cc_id=Case(
                    When(cc_id__isnull=False, then=Value(True)), default=Value(False), output_field=BooleanField()
                )
            )
            .order_by(*order_by_criteria)
        )
        film = next((film for film in all_category_films if film.pk not in picked_film_ids), None)
        if film:
            Pick.objects.create(user=user, year=CURRENT_YEAR, category=category, film=film)
            picked_film_ids.add(film.pk)
            decade_weights.add_to_decade(film.decade)
