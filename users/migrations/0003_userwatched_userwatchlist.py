# Generated by Django 5.1.5 on 2025-01-20 15:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("films", "0001_initial"),
        ("users", "0002_user_date_of_birth"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserWatched",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("films", models.ManyToManyField(blank=True, to="films.film")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="watched", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "verbose_name": "Watched Film",
            },
        ),
        migrations.CreateModel(
            name="UserWatchlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("films", models.ManyToManyField(blank=True, to="films.film")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watchlist",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Watchlisted Film",
            },
        ),
    ]
