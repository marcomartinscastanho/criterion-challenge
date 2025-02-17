from django.db.models import QuerySet

from categories.models import Category
from films.models import Film
from films.utils import filter_films_by_criteria
from users.models import User


def get_category_films(category: Category, user: User):
    if category.films.exists():
        return category.films.all()
    if not category.custom_criteria:
        return Film.objects.none()
    films = Film.objects.all()
    return filter_films_by_criteria(films, category.custom_criteria, user)


def len_or_warning(qs: QuerySet):
    return len(qs) if qs.exists() else "⚠️"
