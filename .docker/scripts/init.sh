#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

if [ "$VENV_DIR" != "" ]; then
  . ${VENV_DIR}/bin/activate
fi
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
ckan_cli db upgrade

CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_DISPLAY_NAME="${CKAN_DISPLAY_NAME:-Administrator}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-Password123!}"
ckan_cli user add "$CKAN_USER_NAME" fullname="$CKAN_DISPLAY_NAME" email="$CKAN_USER_EMAIL" password="$CKAN_USER_PASSWORD"

# Create some base test data
. $APP_DIR/scripts/create-test-data.sh
