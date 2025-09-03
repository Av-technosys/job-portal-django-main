#!/bin/bash
cd /home/avtechnosys02/app/job-portal-django-main
source venv/bin/activate
exec python manage.py runserver 0.0.0.0:8000
