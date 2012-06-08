Applaud
-------

Installation Instructions
=========================

    # Ubuntu 12.04 32bit - 2012-06-07
    # comments start with a hash sign

    sudo apt-get install build-essential
    sudo apt-get install git-core
    sudo apt-get install python-setuptools
    sudo apt-get install postgresql-9.1
    sudo apt-get install postgresql-server-dev-9.1
    sudo apt-get install python-dev
    sudo easy_install virtualenv
    sudo mkdir /srv/applaud

    # USERNAME is a variable you must replace
    sudo chown /srv/applaud USERNAME

    cd /srv/applaud
    virtualenv --no-site-packages venv

    # GITHUB_URL is a variable you must replace
    git clone GITHUB_URL

    ./venv/bin/pip install -r requirements.txt
