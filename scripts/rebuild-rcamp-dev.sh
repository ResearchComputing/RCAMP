#!/bin/bash

export RCAMP_PORT=9000
export HOSTNAME=localhost
export UWSGI_UID=$(id -u)
export UWSGI_GID=$(id -u)

cd $1
docker build -t dev/rcamp --build-arg UWSGI_UID=$UWSGI_UID --build-arg UWSGI_GID=$UWSGI_GID rcamp/
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test-backends.yml down --remove-orphans
cd $1
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test-backends.yml build
