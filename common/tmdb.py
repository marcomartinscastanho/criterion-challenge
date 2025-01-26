from urllib.parse import urlencode

import requests
from django.conf import settings
from ratelimit import limits, sleep_and_retry

MAX_CALLS = 45
ONE_SECONDS = 1
TMDB_API_URL = "https://api.themoviedb.org/3"


@sleep_and_retry
@limits(calls=MAX_CALLS, period=ONE_SECONDS)
def call_tmdb_api(path: str, query_params: dict = {}):
    url = f"{TMDB_API_URL}/{path}"
    if query_params:
        # Handle lists by joining them with commas
        formatted_params = {k: ",".join(v) if isinstance(v, list) else v for k, v in query_params.items()}
        query_string = urlencode(formatted_params)
        url = f"{url}?{query_string}"
    response = requests.get(url, headers={"Authorization": f"Bearer {settings.TMDB_API_TOKEN}"})
    assert response.status_code == 200
    return response.json()


def search_movie(title: str, year: int) -> int:
    body = call_tmdb_api("search/movie", {"query": title, "year": year})
    assert isinstance(body, dict)
    assert "total_results" in body
    assert body["total_results"] >= 1
    assert "results" in body
    results = body["results"]
    assert isinstance(results, list)
    assert len(results) >= 1
    result = results[0]
    assert isinstance(result, dict)
    assert "id" in result
    id = result["id"]
    assert isinstance(id, int)
    return id


def get_movie_details(id: int):
    body = call_tmdb_api(f"movie/{id}", {"append_to_response": "credits"})
    assert isinstance(body, dict)
    # genres
    assert "genres" in body
    r_genres = body["genres"]
    assert isinstance(r_genres, list)
    assert all(isinstance(genre, dict) for genre in r_genres)
    assert all("name" in genre for genre in r_genres)
    assert all(isinstance(genre["name"], str) for genre in r_genres)
    genres: list[str] = [genre["name"] for genre in r_genres]
    # counties
    assert "production_countries" in body
    r_countries = body["production_countries"]
    assert isinstance(r_countries, list)
    assert all(isinstance(country, dict) for country in r_countries)
    assert all(set(country.keys()) == {"iso_3166_1", "name"} for country in r_countries)
    assert all(isinstance(country["iso_3166_1"], str) for country in r_countries)
    assert all(isinstance(country["name"], str) for country in r_countries)
    countries = [{"code": country["iso_3166_1"], "name": country["name"]} for country in r_countries]
    assert "origin_country" in body
    r_origin = body["origin_country"]
    assert isinstance(r_origin, list)
    assert all(isinstance(origin, str) for origin in r_origin)
    countries.extend([{"code": origin} for origin in r_origin])
    # directors
    assert "credits" in body
    r_credits = body["credits"]
    assert isinstance(r_credits, dict)
    assert "crew" in r_credits
    r_crew = r_credits["crew"]
    assert isinstance(r_crew, list)
    assert all(isinstance(crew_credit, dict) for crew_credit in r_crew)
    assert all("name" in crew_credit for crew_credit in r_crew)
    assert all("job" in crew_credit for crew_credit in r_crew)
    assert all(isinstance(crew_credit["name"], str) for crew_credit in r_crew)
    assert all(isinstance(crew_credit["job"], str) for crew_credit in r_crew)
    directors: list[str] = [crew_credit["name"] for crew_credit in r_crew if crew_credit["job"] == "Director"]
    # TODO: runtime

    return {"tmdb_id": id, "genres": genres, "countries": countries, "directors": directors}


def get_film(title: str, year: int):
    tmdb_id = search_movie(title, year)
    movie_details = get_movie_details(tmdb_id)
    return {"title": title, "year": year, **movie_details}
