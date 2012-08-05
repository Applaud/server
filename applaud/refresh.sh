#!/bin/sh

CURDIR=`pwd`

rm ${CURDIR}/applaud/test.db
python manage.py syncdb --noinput
python populate.py

# If we're on a server, make sure permissions are OK
if [ CURDIR = '/var/www/server/applaud' ]
then
    sudo chown www-data:www-data ${CURDIR}/applaud/test.db
fi