#!/bin/bash

export RCAMP_PORT=9000
export HOSTNAME=localhost
export UWSGI_UID=$(id -u)
export UWSGI_GID=$(id -u)

cd $1
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test-backends.yml down --remove-orphans
cd $1
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test-backends.yml build
