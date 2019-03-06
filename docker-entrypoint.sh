#!/bin/bash

STATIC_DIR=/opt/static
MEDIA_DIR=/opt/media
LOG_DIR=/opt/logs
RCAMP_DIR=/opt/rcamp
UWSGI_CONFIG=/opt/uwsgi.ini

# Ensure the uwsgi user and group are set
: ${UWSGI_UID:?"You must set UWSGI_UID to identify the user to run RCAMP."}
: ${UWSGI_GID:?"You must set UWSGI_GID to identify the group to run RCAMP."}

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python manage.py collectstatic --noinput'
chown -R $UWSGI_UID:$UWSGI_GID $STATIC_DIR
chown -R $UWSGI_UID:$UWSGI_GID $MEDIA_DIR
chown -R $UWSGI_UID:$UWSGI_GID $LOG_DIR
chown -R $UWSGI_UID:$UWSGI_GID $RCAMP_DIR
chown $UWSGI_UID:$UWSGI_GID $UWSGI_CONFIG

exec gosu $UWSGI_UID:$UWSGI_GID "$@"
