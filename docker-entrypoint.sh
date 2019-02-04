#!/bin/bash

STATIC_DIR=/home/uwsgi/static
MEDIA_DIR=/home/uwsgi/media
LOG_DIR=/home/uwsgi/logs

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python manage.py collectstatic --noinput'
chown -R uwsgi:uwsgi $STATIC_DIR
chown -R uwsgi:uwsgi $MEDIA_DIR
chown -R uwsgi:uwsgi $LOG_DIR

exec gosu uwsgi "$@"
