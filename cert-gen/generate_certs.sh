#!/bin/sh
openssl genrsa -des3 -passout pass:xxxx -out $CERT_NAME.pass.key 2048
openssl rsa -passin pass:xxxx -in $CERT_NAME.pass.key -out $CERT_NAME.key
rm $CERT_NAME.pass.key
openssl req -new -key $CERT_NAME.key -out $CERT_NAME.csr -subj "/C=US/ST=Colorado/L=Boulder/O=University of Colorado Boulder/OU=Research Computing/CN=${COMMON_NAME}"
openssl x509 -req -days 365 -in $CERT_NAME.csr -signkey $CERT_NAME.key -out $CERT_NAME.crt
