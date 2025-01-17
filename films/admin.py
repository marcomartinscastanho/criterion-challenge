from django.contrib import admin

# Register your models here.
from films.models import Film


class FilmAdmin(admin.ModelAdmin):
    list_display = ["spine", "title", "get_directors", "country", "year"]
    list_display_links = ["title"]
    search_fields = ["title"]
    filter_horizontal = ["directors"]
    exclude = ["cc_id"]

    def get_directors(self, obj: Film):
        return ", ".join([director.name for director in obj.directors.all()])

    get_directors.short_description = "Director"


admin.site.register(Film, FilmAdmin)
