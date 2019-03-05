#!/bin/bash

STATIC_DIR=/opt/static
MEDIA_DIR=/opt/media
LOG_DIR=/opt/logs
RCAMP_DIR=/opt/rcamp
UWSGI_CONFIG=/opt/uwsgi.ini

# Add uwsgi user and group
groupadd -g $UWSGI_GID uwsgi
useradd -d "/home/uwsgi" -u "$UWSGI_UID" -g "$UWSGI_GID" -m -s /bin/bash "uwsgi"

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python manage.py collectstatic --noinput'
chown -R uwsgi:uwsgi $STATIC_DIR
chown -R uwsgi:uwsgi $MEDIA_DIR
chown -R uwsgi:uwsgi $LOG_DIR
chown -R uwsgi:uwsgi $RCAMP_DIR
chown uwsgi:uwsgi $UWSGI_CONFIG

exec gosu uwsgi "$@"
