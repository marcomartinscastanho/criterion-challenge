from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from categories.models import Category
from films.models import Film
from users.models import User


class Pick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="picks")
    year = models.PositiveIntegerField(null=False, validators=[MinValueValidator(2020)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False, related_name="picks")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, null=False, blank=False, related_name="picks")
    watched = models.BooleanField(default=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "category"], name="unique_user_category"),
            models.UniqueConstraint(fields=["user", "year", "film"], name="unique_user_year_film"),
        ]
        ordering = ["category__number"]

    def validate_custom_criteria(self):
        for key, value in dict(self.category.custom_criteria).items():
            if key == "any":
                return
            if key == "year" and value == "user__date_of_birth":
                if self.film.year == self.user.date_of_birth.year:
                    return
                else:
                    raise ValidationError(_("The year of the pick must match the category criteria."))

    def clean(self):
        if self.year != self.category.year:
            raise ValidationError(_("The year of the pick must match the category year."))
        if self.category.custom_criteria:
            self.validate_custom_criteria()
        elif self.film not in self.category.films.all():
            raise ValidationError(_("The selected film must belong to the selected category."))

    def __str__(self):
        return f"Pick by {self.user.username} - {self.category} - {self.film}"

    def save(self, *args, **kwargs):
        if self.pk and Pick.objects.get(pk=self.pk).watched:
            raise ValidationError(_("This pick is already watched and cannot be edited or deleted."))
        super().save(*args, **kwargs)
