@echo off
setlocal

set DJANGO_SETTINGS_MODULE=project.settings_local

py -3 -m pip install -r requirements.txt
py -3 manage.py migrate
py -3 manage.py collectstatic --noinput
py -3 manage.py runserver
