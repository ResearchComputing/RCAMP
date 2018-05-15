#!/bin/bash

STATIC_DIR=/home/uwsgi/rcamp/static
MEDIA_DIR=/home/uwsgi/rcamp/media
LOG_DIR=/home/uwsgi/rcamp/logs

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python manage.py collectstatic --noinput'
chown -R uwsgi:uwsgi $STATIC_DIR
chown -R uwsgi:uwsgi $MEDIA_DIR
chown -R uwsgi:uwsgi $LOG_DIR

exec gosu uwsgi "$@"
