#!/bin/bash

echo "---- Running build_files.sh ----"

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

echo "---- Build complete ----"
