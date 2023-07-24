#!/command/with-contenv /bin/bash

#Default runtime variables if none supplied with -e
UWSGI_UID=${UWSGI_UID:='1000'}
UWSGI_UID=${UWSGI_GID:='1000'}
VIRTUAL_ENV=${VIRTUAL_ENV:='/opt/rcamp_venv'}
STATIC_DIR=${STATIC_DIR:='/opt/static'}
MEDIA_DIR=${MEDIA_DIR:='/opt/media'}
LOG_DIR=${LOG_DIR:='/opt/logs'}
RCAMP_DIR=${RCAMP_DIR:='/opt/rcamp'}
UWSGI_CONFIG=${UWSGI_CONFIG:='/opt/uwsgi.ini'}

printf "$(basename $0): info: Running container startup script...\n"
printf "$(basename $0): info: Set UWSGI_UID and UWSGI_GID...\n"

# Collect static, and set permissions of shared volumes.
RCAMP_DEBUG=True bash -c 'python3 manage.py collectstatic --noinput'
chown -R $UWSGI_UID:$UWSGI_GID $STATIC_DIR
chown -R $UWSGI_UID:$UWSGI_GID $MEDIA_DIR
chown -R $UWSGI_UID:$UWSGI_GID $LOG_DIR
chown -R $UWSGI_UID:$UWSGI_GID $RCAMP_DIR
chown $UWSGI_UID:$UWSGI_GID $UWSGI_CONFIG

printf "$(basename $0): info: End container startup script.\n"

exit 0
