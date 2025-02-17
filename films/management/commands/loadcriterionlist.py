import re

import cloudscraper
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from categories.models import Category
from directors.models import Director
from films.models import Film
from films.utils import enrich_film_details

CRITERION_COLLECTION_URL = "https://www.criterion.com/shop/browse/list?sort=spine_number"


def extract_number_from_url(url):
    match = re.search(r"(films|boxsets)/(\d+)", url)
    if match:
        return match.group(2)
    return None


class Command(BaseCommand):
    help = "Updates the DB with the current Criterion Collection."

    def scrape_website(self, url):
        films = []
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
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
                directors_list = re.split(split_pattern, directors_text.strip())
                directors_list = [director.strip(" …\n\t") for director in directors_list]
                directors_list = [director for director in directors_list if director]  # clean possible empties
            except Exception as e:
                print("ERROR[directors]: ", e)
                directors_list = []
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
            films.append(
                {
                    "cc_id": cc_id,
                    "spine": spine or None,
                    "title": title,
                    "directors": directors_list,
                    "country": country,
                    "year": year or None,
                }
            )
        return films

    def add_films_to_db(self, films: list[dict], category_id: int = None):
        director_objects_map = dict()
        film_objects = []
        for film in films:
            if Film.objects.filter(cc_id=film["cc_id"]).exists():
                film_objects.append(Film.objects.get(cc_id=film["cc_id"]))
                continue
            if not film["year"]:
                print(f"WARNING: ignoring {film} since it has no 'year'")
                continue
            if Film.objects.filter(title=film["title"], year=film["year"]).exists():
                film_objects.append(Film.objects.get(title=film["title"], year=film["year"]))
                continue
            for director_name in film["directors"]:
                director_obj, _ = Director.objects.get_or_create(name=director_name)
                director_objects_map[director_name] = director_obj
            try:
                film_object = Film.objects.create(
                    title=film["title"], year=film["year"], cc_id=film["cc_id"], spine=film["spine"]
                )
                film_object.directors.set([director_objects_map[director] for director in film["directors"]])
                enrich_film_details(film_object)
                film_objects.append(film_object)
            except Exception as e:
                print("ERROR[creating Film]: ", e)
                continue
        if category_id is not None:
            try:
                category = Category.objects.get(pk=category_id)
                category.films.set(film_objects)
                category.save()
            except Category.DoesNotExist as e:
                print("ERROR[updating Category]: ", e)

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            nargs=2,
            action="append",
            metavar=("CATEGORY ID", "CC COLLECTION URL"),
            help="Provide key-value pairs using --category category_id url",
        )

    def handle(self, *args, **options):
        categories = options["category"]
        if categories is None:
            films = self.scrape_website(CRITERION_COLLECTION_URL)
            self.add_films_to_db(films)
        for category_id, url in categories:
            films = self.scrape_website(url)
            self.add_films_to_db(films, category_id)
        print("DONE")
