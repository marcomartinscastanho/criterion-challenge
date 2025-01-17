from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from films.models import Film


class Category(models.Model):
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)], help_text="Enter a number between 1 and 52."
    )
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[MinValueValidator(2020)])
    films = models.ManyToManyField(Film, related_name="categories", blank=False)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("number", "year")
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}: {self.title}"

    @property
    def num_films(self):
        return self.films.count()
