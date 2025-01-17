from django.contrib import admin

# Register your models here.
from films.models import Film


class FilmAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "get_directors"]
    search_fields = ["title"]
    filter_horizontal = ("directors",)  # This adds a dual list widget to select multiple directors

    def get_directors(self, obj: Film):
        return ", ".join([director.name for director in obj.directors.all()])

    get_directors.short_description = "Director"


admin.site.register(Film, FilmAdmin)
