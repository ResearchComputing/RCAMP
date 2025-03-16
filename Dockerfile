# Use Python 3.9 as the base image
FROM python:3.9-slim

# Define gosu version
ARG GOSU_VERSION=1.16

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    lsb-release \
    ca-certificates \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libmariadb-dev \
    libmariadb-dev-compat \
    default-libmysqlclient-dev \
    libldap2-dev \
    libsasl2-dev \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-venv \
    sqlite3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install gosu to drop user and chown shared volumes at runtime
RUN curl -fsSL https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64 -o /usr/bin/gosu \
    && chmod +x /usr/bin/gosu \
    && gosu nobody true

# Set working directory
WORKDIR /opt/rcamp

# Add requirements and other necessary files
ADD ["requirements.txt", "/opt/requirements.txt"]
ADD ["uwsgi.ini", "/opt/uwsgi.ini"]
ADD ["rcamp", "/opt/rcamp"]

# Set up virtual environment
WORKDIR /opt
ENV VIRTUAL_ENV=/opt/rcamp_venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install the dependencies from requirements.txt
COPY requirements.txt /opt/
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt

# fix dep issues
RUN sed -i '/from django.utils import timezone/a from pytz import utc\ntimezone.utc = utc' /opt/rcamp_venv/lib/python3.9/site-packages/ldapdb/models/fields.py
RUN sed -i 's/from django.conf.urls import url/from django.urls import re_path as url/' /opt/rcamp_venv/lib/python3.9/site-packages/grappelli/urls.py

# Clone and install the django-ldapdb-test-env repository
WORKDIR /opt/rcamp

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose necessary ports
EXPOSE 80/tcp
EXPOSE 443/tcp

# Simple Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 CMD curl http://localhost:8000/ || exit 1

# Copy entrypoint script
COPY ["docker-entrypoint.sh", "/usr/local/bin/"]

# Set entrypoint
ENTRYPOINT ["sh", "/usr/local/bin/docker-entrypoint.sh"]

# Default command to start the application
CMD ["/opt/rcamp_venv/bin/uwsgi", "/opt/uwsgi.ini"]

