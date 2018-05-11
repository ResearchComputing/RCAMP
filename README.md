# RCAMP
Research Computing Administrative &amp; Management Portal

## Overview and App Structure

**accounts** - The accounts app contains all code for the creation, review, and approval of account requests. Also contained in this app is all code necessary for managing users and groups.

**projects** - The projects app contains all code for the request and management of projects and compute-time allocations.

**mailer** - The mailer app contains all code for sending emails from app-wide signals.

**endpoints** - The endpoints app exposes a selection of RESTful endpoints for accessing RCAMP data.

**lib** - The lib app contains shared code for the rest of the app.

**rcamp** - The rcamp directory contains site code and, most importantly, settings.

## Setting up your dev environment
You will need Docker 18.03+ and Compose 1.21+ before you begin. Documentation for Docker can be found here: https://docs.docker.com/install/.

Start by cloning RCAMP.
```
$ git clone https://github.com/ResearchComputing/RCAMP
$ git submodule update --init
$ cd RCAMP
```

Then build the RCAMP base image, making sure to pass your local account UID/GID as build args _(this is necessary for bind-mounting your code later)_.
```
$ cd rcamp
$ docker build -t dev/rcamp --build-arg UWSGI_UID=$(id -u) --build-arg UWSGI_GID=$(id -g) .
$ cd ..
```

Build your dev environment and then start it using Compose.
```
$ docker-compose -f docker-compose.yml -f docker-compose.test-backends.yml -f docker-compose.dev.yml build
$ docker-compose -f docker-compose.yml -f docker-compose.test-backends.yml -f docker-compose.dev.yml up -d
```

Finish by migrating the DB and adding a superuser to the RCAMP app. You'll need to attach to the running RCAMP service to do this:
```
$ docker exec -it rcamp_rcamp-uwsgi_1 /bin/bash
~rcamp-uwsgi$ python manage.py migrate
~rcamp-uwsgi$ python manage.py createsuperuser
...
```

## Writing and Running Tests
Documentation on use and installation of the RCAMP test framework can be found in the RCAMP Wiki [Test Framework page](https://github.com/ResearchComputing/RCAMP/wiki/Test-Framework).
