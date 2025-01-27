from films.models import Film
from films.utils import enrich_film_details


def get_tmdb_id(sender, instance: Film, **kwargs):
    if not instance.tmdb_id:
        enrich_film_details(instance)
