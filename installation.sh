#!/bin/sh

# Ubuntu 12.04 32bit - 2012-06-07

username=`whoami`

sudo apt-get install build-essential
sudo apt-get install git-core
sudo apt-get install python-setuptools
sudo apt-get install postgresql-9.1
sudo apt-get install postgresql-server-dev-9.1
sudo apt-get install python-dev
sudo apt-get install postfix
sudo easy_install virtualenv
sudo mkdir /srv/applaud

sudo chown ${username} /srv/applaud

cd /srv/applaud
virtualenv --no-site-packages venv

# GITHUB_URL is a variable you must replace
mkdir server
cd server
git clone https://github.com/Applaud/server.git

./venv/bin/pip install -r requirements.txt