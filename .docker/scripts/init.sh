#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_DISPLAY_NAME="${CKAN_DISPLAY_NAME:-Administrator}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-password}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"

if [ "$VENV_DIR" != "" ]; then
  . ${VENV_DIR}/bin/activate
fi
ckan_cli db clean
ckan_cli db init
ckan_cli user add "${CKAN_USER_NAME}"\
 fullname="${CKAN_DISPLAY_NAME}"\
 email="${CKAN_USER_EMAIL}"\
 password="${CKAN_USER_PASSWORD}"
ckan_cli sysadmin add "${CKAN_USER_NAME}"

# Initialise the Comments database tables
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli initdb
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli updatedb
PASTER_PLUGIN=ckanext-ytp-comments ckan_cli init_notifications_db

# Initialise the archiver database tables
PASTER_PLUGIN=ckanext-archiver ckan_cli archiver init

# Initialise the reporting database tables
PASTER_PLUGIN=ckanext-report ckan_cli report initdb

# Initialise the QA database tables
PASTER_PLUGIN=ckanext-qa ckan_cli qa init

# Create some base test data
. $APP_DIR/scripts/create-test-data.sh
