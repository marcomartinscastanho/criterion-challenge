from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError


def validate_year(value):
    if value <= 2020:
        raise ValidationError("Year must be greater than 2020.")


class Category(models.Model):
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        help_text="Enter a number between 1 and 52.",
    )
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[validate_year])
    films = models.ManyToManyField("films.Film", through="FilmCategory", related_name="categories")

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("number", "year")

    def __str__(self):
        return f"{self.number}: {self.title}"


class FilmCategory(models.Model):
    film = models.ForeignKey("films.Film", on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ("film", "category")

    def __str__(self):
        return f"{self.film} - {self.category}"
