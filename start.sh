#!/usr/bin/env bash

# Run migrations at startup instead of build (Free Tier workaround)
python manage.py migrate

# Seed categories
python manage.py shell -c "from jobs.models import JobCategory; [JobCategory.objects.get_or_create(name=n, slug=n.lower().replace(' ', '-')) for n in ['Bank Jobs', 'Teaching Jobs', 'Railway Jobs', 'Defence Jobs', 'Tech Jobs', 'Medical Jobs', 'Freelance']]"

# Start Gunicorn server
exec gunicorn job_portal.wsgi:application
