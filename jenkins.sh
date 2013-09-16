#!/bin/bash

#
# setup the environment in jenkins
#
virtualenv env
env/bin/pip install -U setuptools
rm src/bioport_repository/bioport_repository/tests/data/bioport_mysqldump.sql -f
env/bin/python bootstrap.py

bin/buildout  -vv -c jenkins.cfg
cd src/bioport_repository/ && git pull && cd ../..
cd src/bioport/ && git pull && cd ../..
cd src/biodes/ && git pull && cd ../..
cd src/names/ && git pull && cd ../..
cd src/gerbrandyutils/ && git pull && cd ../..
mysqladmin drop bioport_test -f
mysqladmin create bioport_test

bin/test
# bin/coveragetest bin/xmltest --xml --no-color
# buildout/bin/coveragexml