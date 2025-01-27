from urllib.parse import urlencode

import requests
from cerberus import Validator
from django.conf import settings
from ratelimit import limits, sleep_and_retry

from common.tmdb.schemas import MOVIE_DETAILS_SCHEMA, SEARCH_MOVIE_SCHEMA

MAX_CALLS = 45
ONE_SECONDS = 1
TMDB_API_URL = "https://api.themoviedb.org/3"


class APIError(Exception):
    """Base class for API-related errors."""

    pass


@sleep_and_retry
@limits(calls=MAX_CALLS, period=ONE_SECONDS)
def call_tmdb_api(path: str, query_params: dict = {}):
    url = f"{TMDB_API_URL}/{path}"
    if query_params:
        formatted_params = {k: ",".join(v) if isinstance(v, list) else v for k, v in query_params.items()}
        query_string = urlencode(formatted_params)
        url = f"{url}?{query_string}"
    response = requests.get(url, headers={"Authorization": f"Bearer {settings.TMDB_API_TOKEN}"})
    if response.status_code != 200:
        raise APIError
    return response.json()


def search_movie(title: str, year: int) -> int:
    v = Validator(SEARCH_MOVIE_SCHEMA, allow_unknown=True)
    body = call_tmdb_api("search/movie", {"query": title, "year": year})
    validated_data = v.validated(body)
    if not validated_data:
        raise ValueError(f"Validation failed: {v.errors}")
    return validated_data["results"][0]["id"]


def get_movie_details(id: int):
    v = Validator(MOVIE_DETAILS_SCHEMA, allow_unknown=True)
    body = call_tmdb_api(f"movie/{id}", {"append_to_response": "credits,keywords"})
    validated_data = v.validated(body)
    if not validated_data:
        raise ValueError(f"Validation failed: {v.errors}")
    countries = [
        {"code": country["iso_3166_1"], "name": country["name"]} for country in validated_data["production_countries"]
    ]
    countries.extend([{"code": origin} for origin in validated_data["origin_country"]])
    directors = [
        crew_credit["name"] for crew_credit in validated_data["credits"]["crew"] if crew_credit["job"] == "Director"
    ]
    genres = [genre["name"] for genre in validated_data["genres"]]
    keywords = [keyword["name"] for keyword in validated_data["keywords"]["keywords"]]
    runtime = validated_data["runtime"]
    return {
        "tmdb_id": id,
        "countries": countries,
        "directors": directors,
        "genres": genres,
        "keywords": keywords,
        "runtime": runtime,
    }


def get_film(title: str, year: int):
    tmdb_id = search_movie(title, year)
    movie_details = get_movie_details(tmdb_id)
    return {"title": title, "year": year, **movie_details}
