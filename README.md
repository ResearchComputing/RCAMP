# RCAMP
Research Computing Administrative &amp; Management Portal

# Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Tests](#tests)
4. [API](#api)

## Overview

**accounts** - The accounts app contains all code for the creation, review, and approval of account requests. Also contained in this app is all code necessary for managing users and groups.

**projects** - The projects app contains all code for the request and management of projects and compute-time allocations.

**mailer** - The mailer app contains all code for sending emails from app-wide signals.

**endpoints** - The endpoints app exposes a selection of RESTful endpoints for accessing RCAMP data.

**lib** - The lib app contains shared code for the rest of the app.

**rcamp** - The rcamp directory contains site code and, most importantly, settings.

## Installation
You will need Docker 18.03+ and Compose 1.21+ before you begin. Documentation for Docker can be found here: https://docs.docker.com/install/.

Start by cloning RCAMP.
```
$ git clone https://github.com/ResearchComputing/RCAMP
$ cd RCAMP
```
Set UWSGI_UID and UWSGI_GID. These are used to match the UID and GID inside and outside of the container, preventing a rebuild every time you need to make changes. 
```
$ id -u $USER
1000
$ export UWSGI_UID=1000

$ id -g $USER
1000
$ export UWSGI_GID=1000
```

Build your dev environment and then start it using Compose.
```
$ docker-compose build
$ docker-compose up -d
```

Finish by migrating the DB and adding a superuser to the RCAMP app. You'll need to attach to the running RCAMP service to do this:
```
$ docker-compose run --rm --entrypoint "python3" rcamp-uwsgi manage.py migrate
$ docker-compose run --rm --entrypoint "python3" rcamp-uwsgi manage.py createsuperuser
```
The name, password, and email needed by the createsuperuser script can be whatever you like. You should now be able to view the webpage at localhost:8000.

## Tests
Documentation on use of the RCAMP test framework can be found in the RCAMP Wiki [Test Framework page](https://github.com/ResearchComputing/RCAMP/wiki/Test-Framework).

```
$ docker-compose run --rm --entrypoint "python3" rcamp-uwsgi manage.py test
```

## API

If your user has superuser permissions, the endpoints can be used for queries. Here are examples of hitting the account requests endpoint

```bash
$ curl -u <username>:<password> "http://rcamp2.rc.int.colorado.edu/api/accountrequests/?min_approve_date=2025-03-15&max_approve_date=2025-03-16"
```
```json
[
  {
    "username": "rmaccuser23",
    "first_name": "rmacc",
    "last_name": "user",
    "email": "rmacc23@user.com",
    "organization": "xsede",
    "discipline": "Visual & Performing Arts",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-15T18:14:14Z",
    "request_date": "2025-03-15T18:14:14Z",
    "notes": ""
  }
]
```

If I want to request all account requests on 2025-03-14
```bash
$ curl -u <user>:<pass> "http://rcamp2.rc.int.colorado.edu/api/accountrequests/?min_approve_date=2025-03-14&max_approve_date=2025-03-15"
```
```json
[
  {
    "username": "rmaccuser14",
    "first_name": "rmacc",
    "last_name": "user",
    "email": "rmaccuser14@cool.com",
    "organization": "xsede",
    "discipline": "Hum",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-14T11:13:15Z",
    "request_date": "2025-03-14T11:13:15Z",
    "notes": ""
  },
  {
    "username": "dahdahdah",
    "first_name": "rmacc",
    "last_name": "user",
    "email": "rmacc255@user.com",
    "organization": "xsede",
    "discipline": "Law",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-14T12:27:11Z",
    "request_date": "2025-03-14T12:27:19Z",
    "notes": ""
  },
  {
    "username": "kyre6371",
    "first_name": "Kyle",
    "last_name": "Reinholt",
    "email": "kyle@Colorado.EDU",
    "organization": "ucb",
    "discipline": "Physical Sciences",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-14T12:29:28Z",
    "request_date": "2025-03-14T12:29:29Z",
    "notes": null
  }
]
```

If you interested in a specific discipline you can use a substring to get results: 
```bash
curl -u <user>:<pass> "http://rcamp2.rc.int.colorado.edu/api/accountrequests/?discipline=Visual"
```
```json
[
  {
    "username": "rmaccuser23",
    "first_name": "rmacc",
    "last_name": "user",
    "email": "rmacc23@user.com",
    "organization": "xsede",
    "discipline": "Visual & Performing Arts",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-15T18:14:14Z",
    "request_date": "2025-03-15T18:14:14Z",
    "notes": ""
  },
  {
    "username": "rmacc-user67",
    "first_name": "rmacc67",
    "last_name": "user67",
    "email": "rmacc67@user.com",
    "organization": "xsede",
    "discipline": "Visual & Performing Arts",
    "course_number": null,
    "sponsor_email": null,
    "resources_requested": null,
    "status": "a",
    "approved_on": "2025-03-16T16:36:00Z",
    "request_date": "2025-03-16T16:36:00Z",
    "notes": ""
  }
]
```
