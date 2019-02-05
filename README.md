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
$ cd RCAMP
```

Build your dev environment and then start it using Compose.
```
$ docker-compose build
$ docker-compose up -d
```

Finish by migrating the DB and adding a superuser to the RCAMP app. You'll need to attach to the running RCAMP service to do this:
```
$ docker-compose exec --entrypoint "python" rcamp-uwsgi manage.py migrate
$ docker-compose exec -it --entrypoint "python" rcamp-uwsgi manage.py createsuperuser
```

## Writing and Running Tests
Documentation on use and installation of the RCAMP test framework can be found in the RCAMP Wiki [Test Framework page](https://github.com/ResearchComputing/RCAMP/wiki/Test-Framework).

```
$ docker-compose run --rm --entrypoint "python" rcamp-uwsgi manage.py test
```
