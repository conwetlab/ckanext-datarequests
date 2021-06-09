#!/usr/bin/env sh
##
# Install current extension.
#
set -e

PIP="${APP_DIR}/bin/pip"
cd $WORKDIR
$PIP install -r "requirements.txt"
$PIP install -r "requirements-dev.txt"
$APP_DIR/bin/python setup.py develop
installed_name=$(grep '^\s*name=' setup.py |sed "s|[^']*'\([-a-zA-Z0-9]*\)'.*|\1|")

# Validate that the extension was installed correctly.
if ! $PIP list | grep "$installed_name" > /dev/null; then echo "Unable to find the extension in the list"; exit 1; fi

