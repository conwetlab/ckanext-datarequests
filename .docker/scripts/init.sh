#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-password}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"

. /app/ckan/default/bin/activate \
  && cd /app/ckan/default/src/ckan \
  && paster db clean -c /app/ckan/default/production.ini \
  && paster db init -c /app/ckan/default/production.ini \
  && paster --plugin=ckan user add "${CKAN_USER_NAME}" email="${CKAN_USER_EMAIL}" password="${CKAN_USER_PASSWORD}" -c /app/ckan/default/production.ini \
  && paster --plugin=ckan sysadmin add "${CKAN_USER_NAME}" -c /app/ckan/default/production.ini

# Initialise the Comments database tables
paster --plugin=ckanext-ytp-comments initdb --config=/app/ckan/default/production.ini

# Initialise the archiver database tables
paster --plugin=ckanext-archiver archiver init --config=/app/ckan/default/production.ini

# Initialise the reporting database tables
paster --plugin=ckanext-report report initdb --config=/app/ckan/default/production.ini

# Initialise the QA database tables
paster --plugin=ckanext-qa qa init --config=/app/ckan/default/production.ini

# Create some base test data
. /app/scripts/create-test-data.sh
