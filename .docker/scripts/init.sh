#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_DISPLAY_NAME="${CKAN_DISPLAY_NAME:-Administrator}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-password}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"

. ${APP_DIR}/bin/activate
CKAN_CLI=$WORKDIR/scripts/ckan_cli
$CKAN_CLI db clean
$CKAN_CLI db init
$CKAN_CLI user add "${CKAN_USER_NAME}"\
 fullname="${CKAN_DISPLAY_NAME}"\
 email="${CKAN_USER_EMAIL}"\
 password="${CKAN_USER_PASSWORD}"
$CKAN_CLI sysadmin add "${CKAN_USER_NAME}"

# Initialise the Comments database tables
PASTER_PLUGIN=ckanext-ytp-comments $CKAN_CLI initdb

# Initialise the archiver database tables
PASTER_PLUGIN=ckanext-archiver $CKAN_CLI archiver init

# Initialise the reporting database tables
PASTER_PLUGIN=ckanext-report $CKAN_CLI report initdb

# Initialise the QA database tables
PASTER_PLUGIN=ckanext-qa $CKAN_CLI qa init

# Create some base test data
. $WORKDIR/scripts/create-test-data.sh
