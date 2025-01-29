from django.db.models import QuerySet
from thefuzz import process

from common.models import Country, Gender, Genre, Keyword, Region
from common.tmdb.tmdb import get_director_details, get_film, get_movie_details
from directors.models import Director
from films.models import Film
from users.models import User

FUZZ_SCORE_CUTOFF = 90


def _is_director_in_list(director: str, film_directors: list[str]):
    return process.extractOne(query=director, choices=film_directors, score_cutoff=FUZZ_SCORE_CUTOFF) is not None


def _is_this_the_correct_film(film: Film, tmdb_data: dict):
    """
    Check if we got the right film from the TDMB search, based on the directors.
    If the film doesn't have any directors, this will always be False.
    Checks:
    1. If any of the returned directors match the film directors by tmdb_id
    2. If any of the returned directors match the film directors by name
    """
    if "directors" not in tmdb_data:
        return False
    if not isinstance(tmdb_data["directors"], list):
        return False
    if not film.directors.exists():
        return False
    # check if any of the returned directors match the film directors by tmdb_id
    film_directors_tmdb_ids = (
        film.directors.exclude(tmdb_id__isnull=True).exclude(tmdb_id="").values_list("tmdb_id", flat=True)
    )
    if len(film_directors_tmdb_ids):
        print(f"[_is_this_the_correct_film] tmdb_data: {tmdb_data}")
        if any(director["tmdb_id"] in film_directors_tmdb_ids for director in tmdb_data["directors"]):
            return True
        print(f"⚠️: {film.pk}: {film.title} ({film.year}) - {tmdb_data['tmdb_id']} directors tmdb_ids don't match.")
        return False
    # check if any of the returned directors match the film directors by name
    film_directors_names = film.directors.values_list("name", flat=True)
    if not any(_is_director_in_list(director["name"], film_directors_names) for director in tmdb_data["directors"]):
        print(f"⚠️: {film.pk}: {film.title} ({film.year}) - {tmdb_data['tmdb_id']} directors names don't match.")
        return False
    return True


def _check_film_matches(film: Film, film_list: list[dict]):
    if film.tmdb_id:
        # check if matches by tmdb_id
        film_list_ids = [dfilm["tmdb_id"] for dfilm in film_list]
        is_id_in_list = film.tmdb_id in film_list_ids
        print(f"[_check_film_matches] Film {film} is in director's filmography (by id)? {is_id_in_list}")
        return is_id_in_list
    # check if matches by title
    film_list_titles = [dfilm["title"] for dfilm in film_list]
    _, score = process.extractOne(query=film.title, choices=film_list_titles)
    is_title_in_list = int(score) >= FUZZ_SCORE_CUTOFF
    print(f"[_check_film_matches] Film {film} is in director's filmography (by title)? {is_title_in_list}")
    return is_title_in_list


def _double_check_director(match_name: str, tmdb_id: int):
    director_details = get_director_details(tmdb_id)
    director_filmography = director_details["films"]
    match_director = Director.objects.filter(name=match_name).first()
    match_films = Film.objects.filter(tmdb_id__isnull=False).filter(directors=match_director)
    all_films_match = all(_check_film_matches(match_film, director_filmography) for match_film in match_films)
    print(f"[_double_check_director] All films of {match_name} match {tmdb_id}? {all_films_match}")
    return all_films_match


def _get_gender(name: str):
    try:
        return Gender.objects.get(name=name)
    except Gender.DoesNotExist:
        return None


def _add_film_directors(film: Film, tmdb_data: dict):
    if "directors" not in tmdb_data:
        return
    print("\n[_add_film_directors]")
    for director_details in tmdb_data["directors"]:
        try:
            # attempt to find the director by tmdb_id
            director = Director.objects.get(tmdb_id=director_details["tmdb_id"])
            print(f"[_add_film_directors] Got the director by tmdb_id: {director}")
        except Director.DoesNotExist:
            # attempt to find the director by name
            all_directors_names = Director.objects.values_list("name", flat=True)
            match, score = process.extractOne(director_details["name"], all_directors_names)
            print(f"[_add_film_directors] match: {match}, score: {score}")
            match_double_checks = _double_check_director(match, director_details["tmdb_id"])
            if score >= FUZZ_SCORE_CUTOFF and match_double_checks:
                # if both the score and the double check are ok, assign the director
                director = Director.objects.get(name=match)
                print(f"[_add_film_directors] Got the director by name: {director}")
                director.tmdb_id = director_details["tmdb_id"]
                if not director.gender:
                    director.gender = _get_gender(director_details["gender"])
                director.save()
            elif score >= FUZZ_SCORE_CUTOFF or match_double_checks:
                # if one of the score or the double check are ok, don't do nothing (uncertainty)
                print(f"[_add_film_directors] Unsure about this director: {director_details}")
                continue
            else:
                # if both the score and the double check are fail, create a new director
                try:
                    director = Director.objects.create(
                        name=director_details["name"],
                        tmdb_id=director_details["tmdb_id"],
                        gender=_get_gender(director_details["gender"]),
                    )
                    print(f"[_add_film_directors] Created the director: {director}")
                except Exception as e:
                    print(f"[_add_film_directors] ERROR creating the director: {e}")
                    # name is unique, which may be a problem -> FIXME: remove uniqueness from director name
                    continue
        film.directors.add(director)


def enrich_film_details(film: Film):
    if not film.title or not film.year:
        return
    try:
        if film.tmdb_id:
            tmdb_data = get_movie_details(film.tmdb_id)
            # FIXME: if not found? (e.g. TV shows...)
        else:
            tmdb_data = get_film(film.title, film.year)
            if not _is_this_the_correct_film(film, tmdb_data):
                return
            # save the tmdb_id
            if "tmdb_id" in tmdb_data and isinstance(tmdb_data["tmdb_id"], int):
                Film.objects.filter(pk=film.pk).update(tmdb_id=tmdb_data["tmdb_id"])
        # from this point on, the film has tmdb_id
        if not film.directors.exists():
            _add_film_directors(film, tmdb_data)
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
            film.refresh_from_db()
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
            Film.objects.filter(pk=film.pk).update(runtime=tmdb_data["runtime"])
    except Exception as e:
        print(f"ERROR: {film.pk}: {film.title} ({film.year}) - {e}")


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
