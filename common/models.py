from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)  # TODO: remove code once the migration is done
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self):
        return self.name
