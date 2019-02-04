FROM centos:7
MAINTAINER Zebula Sampedro <sampedro@colorado.edu>

# Install gosu to drop user and chown shared volumes at runtime
RUN export GOSU_VERSION=1.10 && \
    yum -y install epel-release && \
  	yum -y install wget dpkg && \
  	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" && \
  	wget -O /usr/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" && \
  	wget -O /tmp/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" && \
  	export GNUPGHOME="$(mktemp -d)" && \
  	gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
  	gpg --batch --verify /tmp/gosu.asc /usr/bin/gosu && \
  	rm -r "$GNUPGHOME" /tmp/gosu.asc && \
  	chmod +x /usr/bin/gosu; \
  	gosu nobody true && \
  	yum -y remove wget dpkg && \
  	yum clean all && \
    unset GOSU_VERSION

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

ADD requirements.txt /home/uwsgi/
RUN pip2 install -r requirements.txt

WORKDIR /home/uwsgi/ldapdb
COPY --chown=uwsgi:uwsgi ldapdb /home/uwsgi/ldapdb
RUN pip install -e .

# Add uwsgi conf
COPY --chown=uwsgi:uwsgi uwsgi.ini /home/uwsgi/uwsgi.ini

# Add codebase to container
COPY --chown=uwsgi:uwsgi rcamp /home/uwsgi/rcamp

WORKDIR /home/uwsgi/rcamp
# Set gosu entrypoint and default command
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["sh","/usr/local/bin/docker-entrypoint.sh"]
CMD ["/usr/bin/uwsgi","/home/uwsgi/uwsgi.ini"]
