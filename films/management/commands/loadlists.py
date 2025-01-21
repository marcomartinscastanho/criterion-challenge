import csv

from django.core.management.base import BaseCommand

from categories.models import Category
from films.models import Film


class Command(BaseCommand):
    help = "Updates the DB with the current Criterion Collection."

    def load_letterboxd(self, category_number):
        max_id = 2147483647  # Maximum value for PositiveIntegerField
        existing_ids = set(Film.objects.values_list("cc_id", flat=True))
        available_ids = (id for id in range(max_id, 0, -1) if id not in existing_ids)
        with open(f"{category_number}.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            films = []
            for i, row in enumerate(reader, 1):
                name = row["Name"]
                year = row["Year"]
                url = row["URL"]
                if not all([name, year, url]):
                    continue
                try:
                    film = Film.objects.get(letterboxd=url)
                except Film.DoesNotExist:
                    cc_id = next(available_ids)
                    film = Film.objects.create(cc_id=cc_id, title=name, year=year, letterboxd=url)
                except Film.MultipleObjectsReturned as e:
                    print(f"Multiple objects with url: {url}")
                    raise e
                films.append(film)
            category = Category.objects.get(number=category_number)
            category.films.set(films)
            self.updated += len(films)

    def handle(self, *args, **options):
        self.created = 0
        self.updated = 0
        self.load_letterboxd(29)
        self.load_letterboxd(30)
        print(f"Created {self.created} films.")
        print(f"Updated {self.updated} films.")
