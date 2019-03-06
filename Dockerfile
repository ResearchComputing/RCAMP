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

WORKDIR /opt

# Install core dependencies
RUN yum -y update && \
    yum makecache fast && \
    yum -y groupinstall "Development Tools" && \
    yum -y install epel-release curl which wget && \
    yum -y install sssd pam-devel openssl-devel && \
    yum -y install python-devel python2-pip && \
    yum -y install openldap-devel MySQL-python

ADD requirements.txt /opt/
RUN pip2 install --upgrade pip && \
    pip2 install -r requirements.txt && \
    pip2 install -e git://github.com/ResearchComputing/django-ldapdb.git@v0.5.1#egg=django-ldapdb

# Add uwsgi conf
COPY uwsgi.ini /opt/uwsgi.ini

# Add codebase to container
COPY rcamp /opt/rcamp

WORKDIR /opt/rcamp
# Set gosu entrypoint and default command
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["sh","/usr/local/bin/docker-entrypoint.sh"]
CMD ["/usr/bin/uwsgi", "/opt/uwsgi.ini"]
