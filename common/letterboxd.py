import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry

MAX_CALLS = 2
ONE_SECONDS = 1


@sleep_and_retry
@limits(calls=MAX_CALLS, period=ONE_SECONDS)
def scrape_letterboxd_for_tmdb_id(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tmdb_element = soup.find(attrs={"data-tmdb-id": True})
        if not tmdb_element:
            raise ValueError(f"Could not scrape TMDB ID from page: {url}")
        tmdb_id = tmdb_element["data-tmdb-id"]
        if isinstance(tmdb_id, list):
            raise TypeError(f"Expected a single TMDb ID string, but found a list: {tmdb_id}")
        return tmdb_id
    except requests.exceptions.RequestException as e:
        print(f"Could not get page {url}: {e}")
    except Exception as e:
        print(e)
