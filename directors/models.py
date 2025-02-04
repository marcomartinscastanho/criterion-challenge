from django.db import models

from common.models import Gender


class Director(models.Model):
    name = models.CharField(max_length=200, unique=True)
    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    gender = models.ForeignKey(Gender, related_name="directors", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
