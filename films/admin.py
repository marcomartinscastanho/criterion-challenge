from django.contrib import admin

# Register your models here.
from films.models import Film


class FilmAdmin(admin.ModelAdmin):
    list_display = ["title", "year"]
    search_fields = ["title"]
    filter_horizontal = ("directors",)  # This adds a dual list widget to select multiple directors


admin.site.register(Film, FilmAdmin)
