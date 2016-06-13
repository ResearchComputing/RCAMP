# RCAMP
Research Computing Administrative &amp; Management Portal

## Overview and App Structure

**accounts** - The accounts app contains all code for the creation, review, and approval of account requests. Also contained in this app is all code necessary for managing users and groups.

**projects** - The projects app contains all code for the request and management of projects and compute-time allocations.

**mailer** - The mailer app contains all code for sending emails from app-wide signals.

**endpoints** - The endpoints app exposes a selection of RESTful endpoints for accessing RCAMP data.

**lib** - The lib app contains shared code for the rest of the app.

**rcamp** - The rcamp directory contains site code and, most importantly, settings.

## Installation

Clone RCAMP
```
git clone https://github.com/ResearchComputing/RCAMP
```

Install the RC fork of django-ldapdb
```
git clone https://github.com/ResearchComputing/django-ldapdb
cd django-ldapdb
python setup.py install
```

Install remaining project dependencies
```
cd ../RCAMP
pip install -r requirements.txt
```

Configure local settings. Configuration in `local_settings.py` will override configuration in `settings.py`.
```
cd rcamp/rcamp
touch local_settings.py
# Configure fields in local_settings as needed.
```
Collect static files
```
python manage.py collectstatic
```

Set up the database (SQLite3 preferred for dev/testing).
```
python manage.py migrate
```

Any problems encountered during this phase can normally be rectified by removing all migration files, and running the following commands:
```
python manage.py makemigrations
python manage.py migrate
```

## Running Tests
```
cd RCAMP/rcamp
python manage.py test
```

## Running the Dev Server
The Dev server will be accessible by default at localhost:8000
```
cd RCAMP/rcamp
python manage.py runserver
```
