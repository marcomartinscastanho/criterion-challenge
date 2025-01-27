from thefuzz import process

from common.models import Country, Genre
from common.tmdb.tmdb import get_film, get_movie_details
from films.models import Film


def is_director_in_list(director: str, film_directors: list[str]):
    return process.extractOne(query=director, choices=film_directors, score_cutoff=85) is not None


def enrich_film_details(film: Film):
    if not film.title or not film.year:
        return
    try:
        if film.tmdb_id:
            tmdb_data = get_movie_details(film.tmdb_id)
        else:
            tmdb_data = get_film(film.title, film.year)
        # check if we got the right film
        if not film.tmdb_id and "directors" in tmdb_data and isinstance(tmdb_data["directors"], list):
            film_directors = film.directors.values_list("name", flat=True)
            if not any(is_director_in_list(director, film_directors) for director in tmdb_data["directors"]):
                print(
                    f"WARNING: {film.pk}: {film.title} ({film.year})"
                    f" - {tmdb_data['tmdb_id']} may not be the right film."
                )
                return
        # save the tmdb_id
        if not film.tmdb_id and "tmdb_id" in tmdb_data and isinstance(tmdb_data["tmdb_id"], int):
            film.tmdb_id = tmdb_data["tmdb_id"]
        if "genres" in tmdb_data and isinstance(tmdb_data["genres"], list):
            film_genres = film.genres.values_list("name", flat=True)
            for genre_name in tmdb_data["genres"]:
                if genre_name in film_genres:
                    continue
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                film.genres.add(genre)
        if "countries" in tmdb_data and isinstance(tmdb_data["countries"], list):
            film_countries = film.countries.values_list("code", flat=True)
            for country_dict in tmdb_data["countries"]:
                if "code" not in country_dict:
                    continue
                country_code = country_dict["code"]
                if country_code in film_countries:
                    continue
                try:
                    country = Country.objects.get(code=country_code)
                except Country.DoesNotExist:
                    if "name" not in country_dict:
                        print(
                            f"Film {film.pk}: {film.title} ({film.year}) not completed because Country {country_code} does not exist."
                        )
                        continue
                    coutry_name = country_dict["name"]
                    country = Country.objects.create(code=country_code, name=coutry_name)
                film.countries.add(country)
            if "runtime" in tmdb_data and isinstance(tmdb_data["runtime"], int):
                film.runtime = tmdb_data["runtime"]
        film.save()
    except Exception as e:
        print(f"ERROR: {film.pk}: {film.title} ({film.year}) - {e}")
