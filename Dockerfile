FROM quay.io/rockylinux/rockylinux:8
LABEL maintainer="Adam W Zheng <wazh7587@colorado.edu>"

# Define s6 overlay process supervisor version
#ARG S6_OVERLAY_VERSION=3.1.5.0

# Define gosu version
ARG GOSU_VERSION=1.16

# Install dependencies 
RUN dnf -y install 'dnf-command(config-manager)' \
 && dnf config-manager --set-enabled powertools \
 && dnf -y install epel-release \
 && dnf -y groupinstall "Development Tools" \
 && dnf -y install xz dpkg which sssd pam_radius sqlite pam-devel openssl-devel python3-devel openldap-devel mysql-devel pcre-devel

# Install gosu to drop user and chown shared volumes at runtime
ADD ["https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64", "/usr/bin/gosu"]
ADD ["https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64.asc", "/tmp/gosu.asc"]
RUN gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
 && gpg --batch --verify /tmp/gosu.asc /usr/bin/gosu
RUN chmod +x /usr/bin/gosu \
 && gosu nobody true

# Cleanup
RUN dnf -y update && dnf clean all && rm -rf /var/cache/dnf && > /var/log/dnf.log

# Add s6-overlay process supervisor
#ADD ["https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz", "/tmp"]
#RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
#ADD ["https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz", "/tmp"]
#RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

# Copy s6-supervisor source definition directory into container
#COPY ["etc/s6-overlay/", "/etc/s6-overlay/"]

# Set Workdir
WORKDIR /opt/rcamp

# Add requirements
ADD ["requirements.txt", "/opt/requirements.txt"]

# Add uwsgi conf
ADD ["uwsgi.ini", "/opt/uwsgi.ini"]

# Add codebase to container
ADD ["rcamp", "/opt/rcamp"]

# From old dockerfile
WORKDIR /opt
ENV VIRTUAL_ENV=/opt/rcamp_venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /opt/
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt

RUN git clone -b python3 https://github.com/ResearchComputing/django-ldapdb-test-env
WORKDIR /opt/django-ldapdb-test-env
RUN python3 setup.py install
WORKDIR /opt/rcamp

#Port Metadata
EXPOSE 80/tcp
EXPOSE 443/tcp

#Simple Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 CMD curl http://localhost:8000/ || exit 1

# s6-overlay entrypoint
#ENTRYPOINT ["/init"]

COPY ["docker-entrypoint.sh", "/usr/local/bin/"]
ENTRYPOINT ["sh","/usr/local/bin/docker-entrypoint.sh"]
CMD ["/opt/rcamp_venv/bin/uwsgi", "/opt/uwsgi.ini"]
