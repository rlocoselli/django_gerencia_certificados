@echo off
setlocal

set DJANGO_SETTINGS_MODULE=project.settings_local
set HOST=127.0.0.1
set PORT=8001

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=py -3
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON=python
    ) else (
        echo Python was not found. Install Python 3 first.
        exit /b 1
    )
)

%PYTHON% -m pip install -r requirements.txt
%PYTHON% manage.py migrate
%PYTHON% manage.py collectstatic --noinput

echo Starting local server at http://%HOST%:%PORT%/
%PYTHON% manage.py runserver %HOST%:%PORT%
