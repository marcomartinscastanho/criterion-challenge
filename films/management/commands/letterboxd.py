import csv
import unicodedata

from django.core.management.base import BaseCommand

from films.models import Film


def normalize_text(text: str) -> str:
    """
    Normalize the input text to remove accents and make it comparable.
    """
    if not text:
        return text
    # Normalize to NFD and remove all diacritic marks
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


class Command(BaseCommand):
    help = "Updates the DB with the current Criterion Collection."

    def load_letterboxd(self, filename, uri_key="Letterboxd URI"):
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Name"]
                year = row["Year"]
                uri = row[uri_key]
                if not all([name, year, uri]):
                    continue
                normalized_name = normalize_text(name)
                films = Film.objects.all()
                for film in films:
                    db_normalized_title = normalize_text(film.title)
                    if (
                        db_normalized_title.lower() == normalized_name.lower()
                        and film.year == int(year)
                        and not film.letterboxd
                    ):
                        film.letterboxd = uri
                        film.save()
                        self.updated += 1

    def handle(self, *args, **options):
        self.updated = 0
        self.load_letterboxd("watched.csv")
        self.load_letterboxd("watchlist.csv")
        self.load_letterboxd("all.csv", "URL")
        print(f"Updated {self.updated} film urls.")
