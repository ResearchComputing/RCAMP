FROM centos:7
MAINTAINER Zebula Sampedro <sampedro@colorado.edu>

# Add uwsgi user to the image
ARG UWSGI_UID=1000
ARG UWSGI_GID=1000
# Set env vars from these args, as there is no utility in forcing the user to set them twice in dev.
ENV UID=${UWSGI_UID}
ENV GID=${UWSGI_GID}

RUN groupadd -g $GID uwsgi && \
    useradd -d "/home/uwsgi" -u "$UID" -g "$GID" -m -s /bin/bash "uwsgi"

WORKDIR /home/uwsgi

# Install core dependencies
RUN yum -y update && \
    yum makecache fast && \
    yum -y groupinstall "Development Tools" && \
    yum -y install epel-release curl which wget && \
    yum -y install sssd pam-devel openssl-devel && \
    yum -y install python-devel python2-pip && \
    yum -y install openldap-devel MySQL-python

# Add uwsgi conf
COPY --chown=uwsgi:uwsgi uwsgi.ini /home/uwsgi/uwsgi.ini

# Add codebase to container and install
COPY --chown=uwsgi:uwsgi ldapdb /home/uwsgi/ldapdb
COPY --chown=uwsgi:uwsgi rcamp /home/uwsgi/rcamp

WORKDIR /home/uwsgi/ldapdb
RUN pip install -e .

WORKDIR /home/uwsgi/rcamp
RUN pip2 install -r requirements.txt

# Drop user and finish configuration
USER uwsgi
RUN export RCAMP_DEBUG=True && python manage.py collectstatic --noinput && unset RCAMP_DEBUG
CMD ["/usr/bin/uwsgi","/home/uwsgi/uwsgi.ini"]
