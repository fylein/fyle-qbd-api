#!/bin/bash

# Creating the cache table
python manage.py createcachetable --database cache_db

# Running qcluster server
python manage.py qcluster