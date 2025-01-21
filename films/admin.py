from django.contrib import admin
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from categories.models import Category
from criterionchallenge.utils import get_object_sql_insert
from films.models import Film
from picks.models import Pick
from users.models import UserWatched, UserWatchlist


@admin.action(description="Change cc_id of selected Films to max available")
def change_cc_id_to_max(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Film]):
    """
    Admin action to change the cc_id of selected Film objects to the maximum available ID.
    """
    max_id = 2147483647  # Maximum value for PositiveIntegerField
    existing_ids = set(Film.objects.values_list("cc_id", flat=True))
    available_ids = (id for id in range(max_id, 0, -1) if id not in existing_ids)

    updated_objects = []
    for film in queryset:
        with transaction.atomic():  # Ensure atomicity for the entire operation
            try:
                new_id = next(available_ids)  # Get the next available ID
            except StopIteration:
                modeladmin.message_user(request, "No available IDs left to assign.", level="error")
                return

            # Create a new Film object with the new cc_id
            old_id = film.cc_id
            film.pk = new_id  # Assign the new primary key
            film.save()  # This creates a new object with the updated ID

            old_film = Film.objects.get(cc_id=old_id)
            # Update Film Director
            new_film = Film.objects.get(cc_id=new_id)
            new_film.directors.set(old_film.directors.all())
            # Update Categories
            categories: QuerySet[Category] = old_film.categories.all()
            for category in categories:
                category.films.remove(old_film)
                category.films.add(new_film)
            # Update Picks
            picks: QuerySet[Pick] = old_film.picks.all()
            for pick in picks:
                pick.film = new_film
                pick.save()
            # Update UserWatched
            user_watched = UserWatched.objects.filter(films=old_film)
            for watched in user_watched:
                watched.films.remove(old_film)
                watched.films.add(new_film)
            user_watchlist = UserWatchlist.objects.filter(films=old_film)
            for watchlist in user_watchlist:
                watchlist.films.remove(old_film)
                watchlist.films.add(new_film)
            # # Delete the old object
            Film.objects.filter(cc_id=old_id).delete()

            updated_objects.append((old_id, new_id))

    modeladmin.message_user(request, f"Successfully updated cc_id for {len(updated_objects)} Film objects.")


@admin.action(description="Generate SQL queries")
def generate_sql_inserts(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Film]) -> None:
    queries = []
    for film in queryset.order_by("cc_id"):
        sql_query = get_object_sql_insert(film)
        queries.append(sql_query)

    joined_queries = "<br>".join(queries)
    modeladmin.message_user(request, format_html(f"<pre>{joined_queries}</pre>"))


class FilmAdmin(admin.ModelAdmin):
    list_display = ["cc_id", "spine", "title", "get_directors", "country", "year", "letterboxd_link", "get_categories"]
    list_display_links = ["title"]
    search_fields = ["title", "letterboxd"]
    filter_horizontal = ["directors"]
    actions = [generate_sql_inserts]

    @admin.display(description="Letterboxd", ordering="letterboxd")
    def letterboxd_link(self, obj: Film):
        return format_html('<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>', url=obj.letterboxd)

    @admin.display(description="Director")
    def get_directors(self, obj: Film):
        return ", ".join([director.name for director in obj.directors.all()])

    @admin.display(description="Categories")
    def get_categories(self, obj: Film):
        return f"{obj.current_categories_count}: " + ", ".join([category.title for category in obj.current_categories])


admin.site.register(Film, FilmAdmin)
