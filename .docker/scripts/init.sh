#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-password}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"
export CKAN_INI=/app/ckan/default/production.ini

. /app/ckan/default/bin/activate
/app/scripts/ckan_cli db clean
/app/scripts/ckan_cli db init
/app/scripts/ckan_cli user add "${CKAN_USER_NAME}" email="${CKAN_USER_EMAIL}" password="${CKAN_USER_PASSWORD}"
/app/scripts/ckan_cli sysadmin add "${CKAN_USER_NAME}"

# Initialise the Comments database tables
PASTER_PLUGIN=ckanext-ytp-comments /app/scripts/ckan_cli initdb

# Initialise the archiver database tables
PASTER_PLUGIN=ckanext-archiver /app/scripts/ckan_cli archiver init

# Initialise the reporting database tables
PASTER_PLUGIN=ckanext-report /app/scripts/ckan_cli report initdb

# Initialise the QA database tables
PASTER_PLUGIN=ckanext-qa /app/scripts/ckan_cli qa init

# Create some base test data
. /app/scripts/create-test-data.sh
