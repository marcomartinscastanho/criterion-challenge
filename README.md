# criterion-challenge

## Run locally

### Pre-requisites

- Have Docker installed

### Setup

- Copy `.env.example` to `.env`
- Set a `DJANGO_SECRET_KEY` on `.env`
- Get a [TMDB](https://developer.themoviedb.org/reference/intro/getting-started) API token and set it as `TMDB_API_TOKEN` on `.env`

### Build

- run `docker compose up -d --build`
- check that both the `db` and `web` containers are running

### Create Admin user

- on docker command line, run `python manage.py createsuperuser`
- follow the instructions there

### Access webapp

- website: [localhost:6091](localhost:6091)
- admin: [localhost:6091/admin/](localhost:6091/admin/)
