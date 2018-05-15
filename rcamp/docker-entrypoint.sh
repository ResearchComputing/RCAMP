#!/bin/bash

STATIC_DIR=/home/uwsgi/rcamp/static
MEDIA_DIR=/home/uwsgi/rcamp/media

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python manage.py collectstatic --noinput'
chown -R uwsgi:uwsgi $STATIC_DIR
chown -R uwsgi:uwsgi $MEDIA_DIR

exec gosu uwsgi "$@"
