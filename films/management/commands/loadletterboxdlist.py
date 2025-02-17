import csv
import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from categories.models import Category
from common.letterboxd import scrape_letterboxd_for_tmdb_id
from common.models import Venue
from films.models import Film, FilmSession
from films.utils import enrich_film_details


def get_category(filename: str):
    try:
        match = re.search(r".*category-(\d+)\.csv$", filename)
        if not match:
            return
        category_id = int(match.group(1))
        return Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        print(f"WARNING: Could not find category {category_id}")
        return None


def get_venue(filename: str):
    try:
        match = re.search(r".*cinemateca-(\d+)-(\d+)\.csv$", filename)
        if not match:
            return
        year = int(match.group(1))
        month = int(match.group(2))
        venue = Venue.objects.get(name__iexact="cinemateca")
        return venue, year, month
    except Venue.DoesNotExist:
        print('WARNING: Could not find venue "cinemateca"')
        return None


def create_cinemateca_session(film: Film, venue: Venue, description: str, year: int, month: int):
    if not all([film, venue, description, year, month]):
        print("Missing args")
        return
    datetime_strs = description.split("\n")
    for datetime_str in datetime_strs:
        try:
            pattern = r"(?i)\[(\d{2})\]\s(\d{2})h(\d{2})"
            match = re.search(pattern, datetime_str)
            if not match:
                print(f"ERROR: datetime {datetime_str} does not match pattern {pattern}")
                continue
            day = int(match.group(1))
            hours = int(match.group(2))
            minutes = int(match.group(3))
            dt = datetime(year, month, day, hours, minutes)
            aware_dt = timezone.make_aware(dt)
            FilmSession.objects.create(film=film, venue=venue, datetime=aware_dt)
        except Exception as e:
            print(f"ERROR: could not create session for film {film} on {datetime_str} at {venue} - {e}")


class Command(BaseCommand):
    help = "Adds films to a category from a letterboxd list. Creates the films if needed."

    def add_arguments(self, parser):
        parser.add_argument("filename", nargs="+", type=str, help="An file named in the format <category_id>.csv")

    def handle(self, *args, **options):
        for filename in options["filename"]:
            self.created = 0
            if not filename.lower().endswith(".csv"):
                print(f"ERROR: Invalid file {filename}. File must be a .csv")
                continue
            category = get_category(filename)
            venue, session_year, session_month = get_venue(filename)
            if not any([category, venue]):
                print("ERROR: could not find neither a category nor a venue")
                continue
            try:
                with open(filename, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    films = []
                    for row in reader:
                        name = row["Name"]
                        year = row["Year"]
                        url = row["URL"]
                        description = row["Description"]
                        if not all([name, year, url]):
                            continue
                        try:
                            film = Film.objects.get(letterboxd=url)
                        except Film.DoesNotExist:
                            tmdb_id = scrape_letterboxd_for_tmdb_id(url)
                            if not tmdb_id:
                                print(f"Skipping {name} ({year}) - tmdb_id not found in letterboxd page")
                                continue
                            film = Film.objects.create(title=name, year=year, letterboxd=url, tmdb_id=tmdb_id)
                            enrich_film_details(film)
                            self.created += 1
                        except Film.MultipleObjectsReturned:
                            print(f"ERROR: Multiple objects with url: {url}")
                            continue
                        films.append(film)
                        # create film session
                        if venue.name == "Cinemateca":
                            create_cinemateca_session(film, venue, description, session_year, session_month)
                    print(f"Created {self.created} films.")
                    category.films.set(films)
                    print(f"Added {len(films)} films to category {category}")
            except Exception as e:
                print(f"ERROR: Failed to load filename {filename} - {e}")
