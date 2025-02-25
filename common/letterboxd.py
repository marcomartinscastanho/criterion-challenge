import re

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from ratelimit import limits, sleep_and_retry

from films.models import Film
from films.utils import enrich_film_details

MAX_CALLS = 2
ONE_SECONDS = 1


@sleep_and_retry
@limits(calls=MAX_CALLS, period=ONE_SECONDS)
def scrape_letterboxd_film_page(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract the Letterboxd filmId
        script_tag = soup.find("script", string=re.compile("data.production.filmId"))
        if not script_tag:
            raise ValueError("Could not find the filmId in the page script.")
        film_id_match = re.search(r"data\.production\.filmId\s*=\s*(\d+);", script_tag.string)
        if not film_id_match:
            raise ValueError("Could not extract filmId.")
        letterboxd_id = film_id_match.group(1)
        body = soup.find("body")
        if not body:
            raise ValueError("Could not find body.")
        tmdb_id = body.get("data-tmdb-id")
        if isinstance(tmdb_id, list):
            raise TypeError(f"Expected a single TMDb ID string, but found a list: {tmdb_id}")
        details = body.find("div", class_="details")
        if not details:
            raise ValueError("Could not extract details.")
        name = details.find("span", class_="name").get_text()
        releaseyear = details.find("div", class_="releaseyear")
        if not releaseyear:
            raise ValueError("Could not find releaseyear.")
        year = releaseyear.find("a").get_text()
        return {"title": name, "year": year, "letterboxd_id": letterboxd_id, "tmdb_id": tmdb_id}
    except requests.exceptions.RequestException as e:
        print(f"Could not get page {url}: {e}")
        return {}
    except Exception as e:
        print(e)
        return {}


@sleep_and_retry
@limits(calls=MAX_CALLS, period=ONE_SECONDS)
def scrape_letterboxd_list_page(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching {url}, status code {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    film_items: ResultSet[Tag | None] = soup.find_all("li", class_="poster-container")
    if not film_items:
        print("No films found, assuming the last page has been reached.")
        return
    film_ids = []
    for outer_item in film_items:
        item = outer_item.find("div", class_="film-poster")
        if not item:
            continue
        data_type = item.get("data-type")
        if data_type != "film":
            print("Not a film.")
            continue
        film_id = item.get("data-film-id")
        if not film_id:
            print("Could not find Letterboxd ID.")
            continue
        try:
            film = Film.objects.get(letterboxd_id=film_id)
        except Film.DoesNotExist:
            film_link = item.get("data-target-link")
            if not film_id:
                print("Could not find Letterboxd url.")
                continue
            film_url = f"https://letterboxd.com{film_link}"
            letterboxd_data = scrape_letterboxd_film_page(film_url)
            tmdb_id = letterboxd_data.get("tmdb_id")
            if not tmdb_id:
                print(f"Skipping {film_url} - tmdb_id not found in letterboxd page")
                continue
            title = letterboxd_data.get("title")
            year = letterboxd_data.get("year")
            film = Film.objects.create(
                title=title, year=year, letterboxd_url=film_url, letterboxd_id=film_id, tmdb_id=tmdb_id
            )
            enrich_film_details(film)
        film_ids.append(film.pk)
    return film_ids
