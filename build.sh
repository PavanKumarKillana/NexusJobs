#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Seed categories
python manage.py shell -c "from jobs.models import JobCategory; [JobCategory.objects.get_or_create(name=n, slug=n.lower().replace(' ', '-')) for n in ['Bank Jobs', 'Teaching Jobs', 'Railway Jobs', 'Defence Jobs', 'Tech Jobs', 'Medical Jobs', 'Freelance']]"
