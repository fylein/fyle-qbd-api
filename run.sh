#!/bin/bash

# Creating the cache table
python manage.py createcachetable --database cache_db

# Running Migrations
python manage.py migrate

# Running qcluster server
python manage.py runserver 0.0.0.0:8008