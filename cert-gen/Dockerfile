FROM alpine:3.7
MAINTAINER Zebula Sampedro <sampedro@colorado.edu>

ARG common_name=localhost
ARG cert_name=ssl
ENV COMMON_NAME=${common_name}
ENV CERT_NAME=${cert_name}

RUN apk add --no-cache --update openssl
COPY generate_certs.sh /usr/local/bin/generate_certs

# Generate self-signed certs
VOLUME /home/root/certs
WORKDIR /home/root/certs
CMD ["sh","/usr/local/bin/generate_certs"]
