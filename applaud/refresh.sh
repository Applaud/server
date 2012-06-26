#!/bin/sh

CURDIR=`pwd`

rm ${CURDIR}/applaud/test.db
python manage.py syncdb --noinput
python populate.py

