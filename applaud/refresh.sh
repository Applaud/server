#!/bin/sh

CURDIR=`pwd`

rm ${CURDIR}/applaud/test.db
python manage.py syncdb --noinput
python seed_content.py

# If we're on a server, make sure permissions are OK
if [ `pwd | cut -c1-9` = "/var/www/" ]; then
    sudo chown -R www-data:www-data /var/www
fi