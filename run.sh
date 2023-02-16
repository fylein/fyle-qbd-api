#!/bin/bash

# Creating the cache table
python manage.py createcachetable --database cache_db

# Running Migrations
python manage.py migrate

# Running qcluster server
gunicorn -c gunicorn_config.py quickbooks_desktop_api.wsgi -b 0.0.0.0:8000
