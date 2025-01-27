from django.db.models import QuerySet
from thefuzz import process

from common.models import Country, Gender, Genre, Keyword, Region
from common.tmdb.tmdb import get_film, get_movie_details
from directors.models import Director
from films.models import Film
from users.models import User


def is_director_in_list(director: str, film_directors: list[str]):
    return process.extractOne(query=director, choices=film_directors, score_cutoff=85) is not None


def enrich_film_details(film: Film):
    if not film.title or not film.year:
        return
    try:
        if film.tmdb_id:
            tmdb_data = get_movie_details(film.tmdb_id)
        else:
            tmdb_data = get_film(film.title, film.year)
        # check if we got the right film
        if not film.tmdb_id and "directors" in tmdb_data and isinstance(tmdb_data["directors"], list):
            film_directors = film.directors.values_list("name", flat=True)
            if not any(is_director_in_list(director, film_directors) for director in tmdb_data["directors"]):
                print(
                    f"WARNING: {film.pk}: {film.title} ({film.year})"
                    f" - {tmdb_data['tmdb_id']} may not be the right film."
                )
                return
        # save the tmdb_id
        if not film.tmdb_id and "tmdb_id" in tmdb_data and isinstance(tmdb_data["tmdb_id"], int):
            film.tmdb_id = tmdb_data["tmdb_id"]
        if "countries" in tmdb_data and isinstance(tmdb_data["countries"], list):
            film_countries = film.countries.values_list("code", flat=True)
            for country_dict in tmdb_data["countries"]:
                if "code" not in country_dict:
                    continue
                country_code = country_dict["code"]
                if country_code in film_countries:
                    continue
                try:
                    country = Country.objects.get(code=country_code)
                except Country.DoesNotExist:
                    if "name" not in country_dict:
                        print(
                            f"Film {film.pk}: {film.title} ({film.year}) not completed because Country {country_code} does not exist."
                        )
                        continue
                    coutry_name = country_dict["name"]
                    country = Country.objects.create(code=country_code, name=coutry_name)
                film.countries.add(country)
        if "genres" in tmdb_data and isinstance(tmdb_data["genres"], list):
            film_genres = film.genres.values_list("name", flat=True)
            for genre_name in tmdb_data["genres"]:
                if genre_name in film_genres:
                    continue
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                film.genres.add(genre)
        if "keywords" in tmdb_data and isinstance(tmdb_data["keywords"], list):
            film_keywords = film.keywords.values_list("name", flat=True)
            for keyword_name in tmdb_data["keywords"]:
                if keyword_name in film_keywords:
                    continue
                keyword, _ = Keyword.objects.get_or_create(name=keyword_name)
                film.keywords.add(keyword)
        if "runtime" in tmdb_data and isinstance(tmdb_data["runtime"], int):
            film.runtime = tmdb_data["runtime"]
        film.save()
    except Exception as e:
        print(f"ERROR: {film.pk}: {film.title} ({film.year}) - {e}")


# FIXME: because this takes a QuerySet[Film] and returns a QuerySet[Film],
# FIXME: this can probably me moved to the Film custom QuerySet class
def filter_films_by_criteria(queryset: QuerySet[Film], criteria: dict, user: User = None):
    for attribute, rules in criteria.items():
        for rule in rules:
            queryset = apply_rule(queryset, attribute, rule, user)
    return queryset


def apply_rule(queryset: QuerySet[Film], attribute: str, rule: dict, user: User = None):
    operation = rule["operation"]
    value = rule["value"]
    if operation == "eq":
        return queryset.filter(**{attribute: resolve_value(value, user)})
    elif operation == "gt":
        return queryset.filter(**{f"{attribute}__gt": resolve_value(value, user)})
    elif operation == "lt":
        return queryset.filter(**{f"{attribute}__lt": resolve_value(value, user)})
    elif operation == "gte":
        return queryset.filter(**{f"{attribute}__gte": resolve_value(value, user)})
    elif operation == "lte":
        return queryset.filter(**{f"{attribute}__lte": resolve_value(value, user)})
    elif operation == "in":
        return queryset.filter(**{f"{attribute}__in": resolve_value(value, user)}).distinct()
    elif operation == "not_in":
        return queryset.exclude(**{f"{attribute}__in": resolve_value(value, user)})
    elif operation == "contains":
        return queryset.filter(**{f"{attribute}__contains": resolve_value(value, user)})
    elif operation == "is_null":
        return queryset.filter(**{f"{attribute}__isnull": resolve_value(value, user)})
    return queryset


def resolve_value(value: dict, user: User = None):
    if "literal" in value:
        return str(value["literal"])
    if "number" in value:
        return int(value["number"])
    if "boolean" in value:
        return bool(value["boolean"])
    if "user_attribute" in value and user:
        return resolve_user_attribute(user, value["user_attribute"])
    if "foreign_key" in value:
        return resolve_foreign_key(value["foreign_key"], value["value"])
    return value


def resolve_user_attribute(user: User, attribute: str):
    attribute_path = attribute.split(".")
    value = user
    try:
        for att in attribute_path:
            if att == "date_of_birth":
                value = value.date_of_birth.year
            elif att == "watched":
                value = value.watched
            elif att == "watchlist":
                value = value.watchlist
            elif att == "films":
                value = value.films.all()
            elif att == "directors":
                value = Director.objects.filter(films__in=value).distinct()
    except Exception:
        return None
    return value


def resolve_foreign_key(fk: str, query: dict):
    key = query["key"]
    value = query["value"]
    if fk == "directors":
        try:
            return Director.objects.get(**{key: value})
        except Director.DoesNotExist:
            return Director.objects.none()
    if fk == "genders":
        try:
            gender = Gender.objects.get(**{key: value})
            return Director.objects.filter(gender=gender)
        except Gender.DoesNotExist:
            return Director.objects.none()
    if fk == "genres":
        if isinstance(value, list):
            return Genre.objects.filter(**{f"{key}__in": value})
        try:
            return Genre.objects.get(**{key: value})
        except Genre.DoesNotExist:
            return Genre.objects.none()
    if fk == "keywords":
        if isinstance(value, list):
            return Keyword.objects.filter(**{f"{key}__in": value})
        try:
            return Keyword.objects.get(**{key: value})
        except Keyword.DoesNotExist:
            return Keyword.objects.none()
    if fk == "regions":
        try:
            region = Region.objects.get(**{key: value})
            return Country.objects.filter(regions=region)
        except Region.DoesNotExist:
            return Country.objects.none()
    return None
