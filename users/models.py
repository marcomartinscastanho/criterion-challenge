from django.contrib.auth.models import AbstractUser
from django.db import models

from films.models import Film


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)


class UserLists(models.Model):
    films = models.ManyToManyField(Film, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def num_films(self):
        return self.films.count()


class UserWatched(UserLists):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="watched")

    class Meta:
        verbose_name = "User Watched List"
        verbose_name_plural = "Watched Films"


class UserWatchlist(UserLists):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="watchlist")

    class Meta:
        verbose_name = "User Watchlist"
        verbose_name_plural = "Watchlisted Films"
