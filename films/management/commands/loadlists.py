import csv

from django.core.management.base import BaseCommand

from categories.models import Category
from films.models import Film


class Command(BaseCommand):
    help = "Updates the DB with the current Criterion Collection."

    def load_letterboxd(self, category_id):
        category = Category.objects.get(pk=category_id)
        with open(f"{category_id}.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            films = []
            for row in reader:
                name = row["Name"]
                year = row["Year"]
                url = row["URL"]
                if not all([name, year, url]):
                    continue
                try:
                    film = Film.objects.get(letterboxd=url)
                except Film.DoesNotExist:
                    film = Film.objects.create(title=name, year=year, letterboxd=url)
                    self.created += 1
                except Film.MultipleObjectsReturned:
                    print(f"Multiple objects with url: {url}")
                    continue
                films.append(film)
            category.films.set(films)
            self.added += len(films)

    def handle(self, *args, **options):
        self.created = 0
        self.added = 0
        self.load_letterboxd(29)
        print(f"Created {self.created} films.")
        print(f"Added {self.added} films to category.")
