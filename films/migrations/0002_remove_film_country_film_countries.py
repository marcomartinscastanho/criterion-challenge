# Generated by Django 5.1.5 on 2025-01-24 15:22

from django.db import migrations, models
from django.db.models import Q

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


def migrate_countries(apps, schema_editor):
    Film = apps.get_model("films", "Film")
    Country = apps.get_model("common", "Country")

    country_objects = {code: Country.objects.create(code=code, name=name) for code, name in COUNTRY_CHOICES}
    for film in Film.objects.filter(~Q(country__isnull=True)):
        if film.country in country_objects:
            film.countries.add(country_objects[film.country])
        film.country = None


def reverse_migration(apps, schema_editor):
    Film = apps.get_model("films", "Film")
    for film in Film.objects.all():
        countries = film.countries.all()
        if countries.exists():
            film.country = countries.first().code
        film.save()


class Migration(migrations.Migration):
    dependencies = [("common", "0001_initial"), ("films", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="film", name="countries", field=models.ManyToManyField(related_name="films", to="common.country")
        ),
        migrations.RunPython(migrate_countries, reverse_migration),
        migrations.RemoveField(model_name="film", name="country"),
    ]
