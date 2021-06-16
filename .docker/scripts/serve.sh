#!/usr/bin/env sh
set -e

dockerize -wait tcp://postgres:5432 -timeout 1m
dockerize -wait tcp://solr:8983 -timeout 1m

sed -i "s@SITE_URL@${SITE_URL}@g" $CKAN_INI

if [ "$VENV_DIR" != "" ]; then
  . ${VENV_DIR}/bin/activate
fi
if (which ckan > /dev/null); then
    ckan -c ${CKAN_INI} run
else
    paster serve ${CKAN_INI}
fi
