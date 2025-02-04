from thefuzz import process

from common.models import Gender
from common.tmdb.tmdb import search_director
from directors.models import Director


def is_film_in_list(film: str, director_films: list[str]):
    return process.extractOne(query=film, choices=director_films, score_cutoff=85) is not None


def enrich_director_details(director: Director):
    if not director.name:
        return
    if director.tmdb_id and director.gender:
        return
    try:
        tmdb_data = search_director(director.name)
        tmdb_id = tmdb_data["tmdb_id"]
        if director.tmdb_id:
            if director.tmdb_id != tmdb_id:
                raise ValueError(f'Person {tmdb_id}:"{director.name}" may not be who we need.')
        else:
            # check if we got the right director
            if tmdb_data["known_for_department"] != "Directing":
                raise ValueError(f'Person {tmdb_id}:"{director.name}" may not be a director.')
            if not any(is_film_in_list(film.title, tmdb_data["films"]) for film in director.films.all()):
                raise ValueError(f'Person {tmdb_id}:"{director.name}" may not be the director we\'re looking for.')
            # tmdb_id
            if not director.tmdb_id and isinstance(tmdb_data["tmdb_id"], int):
                director.tmdb_id = tmdb_data["tmdb_id"]
        # gender
        if "gender" in tmdb_data and isinstance(tmdb_data["gender"], str):
            gender = Gender.objects.get(name=tmdb_data["gender"])
            director.gender = gender
        director.save()
    except Exception as e:
        print(f"ERROR: {director.pk}: {director.name} - {e}")
