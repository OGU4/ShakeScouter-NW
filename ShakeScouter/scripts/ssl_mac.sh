#!/bin/bash

HOSTNAME='localhost'

ENVFILE='../.env'
ENVSAMPLE_FILE='../.env.sample'

DEVDIR='../.dev'
SSLDIR="$DEVDIR/ssl"

# Check mkcert
if ! brew ls --versions mkcert > /dev/null; then
	brew install mkcert --dry-run
	mkcert -install
fi

# Check directories
if [ ! -d $DEVDIR ]; then
	mkdir $DEVDIR
fi
if [ ! -d $SSLDIR ]; then
	mkdir $SSLDIR
fi

# Create SSL server certificate
mkcert $HOSTNAME

# Move files
mv "$HOSTNAME.pem" "$SSLDIR/$HOSTNAME.crt"
mv "$HOSTNAME-key.pem" "$SSLDIR/$HOSTNAME.key"

# Copy `.env` if not exists
if [ ! -e $ENVFILE ]; then
	cp $ENVSAMPLE_FILE $ENVFILE
fi

# Write SSL files
echo "WS_SSLCERT=$SSLDIR/$HOSTNAME.crt" >> $ENVFILE
echo "WS_SSLKEY=$SSLDIR/$HOSTNAME.key"  >> $ENVFILE
