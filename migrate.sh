#!/bin/bash

source .env
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate "$@"