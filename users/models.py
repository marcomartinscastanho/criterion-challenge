from django.contrib.auth.models import AbstractUser
from django.db import models

from films.models import Film


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)


class UserWatched(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="watched")
    films = models.ManyToManyField(Film, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Watched Film"


class UserWatchlist(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="watchlist")
    films = models.ManyToManyField(Film, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Watchlisted Film"
