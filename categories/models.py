import json

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from films.models import Film


class Category(models.Model):
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)], help_text="Enter a number between 1 and 52."
    )
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[MinValueValidator(2020)])
    films = models.ManyToManyField(Film, related_name="categories", blank=True)
    custom_criteria = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("number", "year")
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}: {self.title}"

    @property
    def num_films(self):
        return self.films.count()

    def clean(self):
        """Custom validation to enforce rules for films and custom_criteria."""

        if self.films.exists() and self.custom_criteria:
            raise ValidationError("Films and custom criteria cannot both be set at the same time.")

        if self.custom_criteria:
            try:
                json.dumps(self.custom_criteria)
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Invalid JSON in custom_criteria: {e}")

    def save(self, *args, **kwargs):
        """Override save to ensure the custom validation is called."""
        self.clean()
        super().save(*args, **kwargs)
