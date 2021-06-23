#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

if [ "$VENV_DIR" != "" ]; then
  . ${VENV_DIR}/bin/activate
fi
ckan_cli db clean
ckan_cli db init

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
