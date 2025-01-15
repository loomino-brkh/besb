#!/bin/bash
source /app/support/venv/bin/activate
cd /app/django_auth

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
#python manage.py shell <<EOF
#from django.contrib.auth import get_user_model
#User = get_user_model()
#if not User.objects.filter(username='admin').exists():
#    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
#EOF

# Collect static files
python manage.py collectstatic --noinput

# Ensure logs directory exists
mkdir -p /app/support/logs

# Run with gunicorn
exec gunicorn auth_project.wsgi:application \
    --bind 0.0.0.0:8001 \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level=debug \
    --access-logformat='%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s %(p)s "%(M)s"' \
    --forwarded-allow-ips='*' \
    --reload
