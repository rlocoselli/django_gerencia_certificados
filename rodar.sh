#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=project.settings_local

python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py runserver
