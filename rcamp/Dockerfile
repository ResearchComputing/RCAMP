FROM centos:7
MAINTAINER Zebula Sampedro <sampedro@colorado.edu>

# Add uwsgi user to the image
ARG USER=uwsgi
ARG GROUP=uwsgi
ARG UID=1000
ARG GID=1000
ARG HOMEDIR=/home/${USER}

RUN groupadd -g ${GID} ${GROUP} && \
    useradd -d "${HOMEDIR}" -u "${UID}" -g "${GID}" -m -s /bin/bash "${USER}"

WORKDIR ${HOMEDIR}

# Install core dependencies
RUN yum -y update && \
    yum makecache fast && \
    yum -y groupinstall "Development Tools" && \
    yum -y install epel-release curl which wget && \
    yum -y install python-devel python2-pip && \
    yum -y install openldap-devel

# Add uwsgi conf
ADD uwsgi.ini /opt/uwsgi.ini

# Add codebase to container and install
ADD ldapdb /opt/ldapdb
ADD rcamp /opt/rcamp
RUN chown -R ${USER}:${GROUP} /opt/ldapdb && \
    chown -R ${USER}:${GROUP} /opt/rcamp && \
    cd /opt/ldapdb && \
    python setup.py install && \
    cd /opt/rcamp && \
    pip2 install -r requirements.txt && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput

# Drop user and set cmd
USER ${USER}
CMD ["/usr/bin/uwsgi","/opt/uwsgi.ini"]
