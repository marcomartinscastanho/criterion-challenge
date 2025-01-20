from math import floor

from django.core.validators import MinValueValidator
from django.db import models

from criterionchallenge.constants import CURRENT_YEAR
from directors.models import Director


class Film(models.Model):
    COUNTRY_CHOICES = [
        ("AO", "Angola"),
        ("AR", "Argentina"),
        ("AU", "Australia"),
        ("AT", "Austria"),
        ("BD", "Bangladesh"),
        ("BE", "Belgium"),
        ("BR", "Brazil"),
        ("CM", "Cameroon"),
        ("CA", "Canada"),
        ("CN", "China"),
        ("CU", "Cuba"),
        ("CZ", "Czechoslovakia"),
        ("DK", "Denmark"),
        ("ET", "Ethiopia"),
        ("FI", "Finland"),
        ("FR", "France"),
        ("DE", "Germany"),
        ("GR", "Greece"),
        ("GT", "Guatemala"),
        ("HK", "Hong Kong"),
        ("HU", "Hungary"),
        ("IS", "Iceland"),
        ("IN", "India"),
        ("ID", "Indonesia"),
        ("IR", "Iran"),
        ("IE", "Ireland"),
        ("IT", "Italy"),
        ("JP", "Japan"),
        ("KZ", "Kazakhstan"),
        ("LS", "Lesotho"),
        ("MX", "Mexico"),
        ("MA", "Morocco"),
        ("NZ", "New Zealand"),
        ("NG", "Nigeria"),
        ("NO", "Norway"),
        ("PH", "Philippines"),
        ("PL", "Poland"),
        ("PT", "Portugal"),
        ("MK", "Republic of Macedonia"),
        ("RO", "Romania"),
        ("SN", "Senegal"),
        ("KR", "South Korea"),
        ("SU", "Soviet Union"),
        ("ES", "Spain"),
        ("SE", "Sweden"),
        ("CH", "Switzerland"),
        ("TW", "Taiwan"),
        ("TH", "Thailand"),
        ("TR", "Turkey"),
        ("UA", "Ukraine"),
        ("GB", "United Kingdom"),
        ("US", "United States"),
        ("WG", "West Germany"),
        ("YU", "Yugoslavia"),
    ]
    cc_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    spine = models.PositiveIntegerField(null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1870)])
    country = models.CharField(max_length=2, null=True, choices=COUNTRY_CHOICES)
    directors = models.ManyToManyField(Director, related_name="films")
    letterboxd = models.URLField(max_length=200)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def decade(self):
        return 10 * floor(self.year / 10)

    @property
    def current_categories(self):
        return self.categories.filter(year=CURRENT_YEAR)

    @property
    def current_categories_count(self):
        return self.categories.filter(year=CURRENT_YEAR).count()
