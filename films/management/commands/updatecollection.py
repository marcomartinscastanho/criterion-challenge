import re

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

from directors.models import Director
from films.models import Film

CRITERION_COLLECTION_URL = "https://www.criterion.com/shop/browse/list?sort=spine_number"


def extract_number_from_url(url):
    match = re.search(r"(films|boxsets)/(\d+)", url)
    if match:
        return match.group(2)
    return None


class Command(BaseCommand):
    help = "Updates the DB with the current Criterion Collection."

    def scrape_website(self):
        self.directors = set()
        self.films = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        cookies = {"cf_clearance": settings.CRITERION_CF_CLEARANCE}
        response = requests.get(CRITERION_COLLECTION_URL, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.content, "html.parser")
        for film_item in soup.find_all("tr", class_="gridFilm"):
            href: str = film_item.get("data-href")
            if "criterion.com/boxsets/" in href:
                continue
            cc_id = extract_number_from_url(href)
            try:
                spine = film_item.find("td", class_="g-spine").get_text(strip=True)
            except Exception as e:
                print("ERROR[spine]: ", e)
                spine = None
            title = film_item.find("td", class_="g-title").get_text(strip=True)
            try:
                directors_text: str = film_item.find("td", class_="g-director").get_text(strip=True)
                directors_text = directors_text.replace("\xa0", " ")
                split_pattern = r",\s+and\s+|,\s+| and "
                directors = re.split(split_pattern, directors_text.strip())
                directors = [director.strip(" …\n\t") for director in directors]
                directors = [director for director in directors if director]  # clean possible empties
                self.directors.update(directors)
            except Exception as e:
                print("ERROR[directors]: ", e)
                directors = []
            try:
                country = film_item.find("td", class_="g-country").get_text(strip=True).strip(",")
            except Exception as e:
                print("ERROR[country]: ", e)
                country = None
            try:
                year = film_item.find("td", class_="g-year").get_text(strip=True)
            except Exception as e:
                print("ERROR[year]: ", e)
                year = None
            self.films.append(
                {
                    "cc_id": cc_id,
                    "spine": spine or None,
                    "title": title,
                    "directors": directors,
                    "country": country,
                    "year": year or None,
                }
            )

    def update_database(self):
        director_objects_map = dict()
        for director_name in self.directors:
            director_obj, _ = Director.objects.get_or_create(name=director_name)
            director_objects_map[director_name] = director_obj
        country_map = dict(Film.COUNTRY_CHOICES)
        country_name_to_code = {name: code for code, name in country_map.items()}
        for film in self.films:
            country_code = country_name_to_code.get(film["country"], None)
            film_obj, _ = Film.objects.update_or_create(
                cc_id=film["cc_id"],
                defaults={
                    "spine": film["spine"],
                    "title": film["title"],
                    "country": country_code,
                    "year": film["year"],
                },
            )
            film_obj.directors.set([director_objects_map[director] for director in film["directors"]])

    def handle(self, *args, **options):
        self.scrape_website()
        self.update_database()
        print(f"Added/updated {len(self.films)} films and {len(self.directors)} directors.")
