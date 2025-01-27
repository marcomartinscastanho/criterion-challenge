from django.apps import AppConfig


class FilmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "films"

    def ready(self):
        from django.db.models.signals import post_save

        from films.models import Film
        from films.signals import get_tmdb_id

        post_save.connect(get_tmdb_id, Film)
