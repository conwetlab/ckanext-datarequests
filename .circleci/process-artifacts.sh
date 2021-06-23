#!/usr/bin/env bash
##
# Process test artifacts.
#
set -e

# Create screenshots directory in case it was not created before. This is to
# avoid this script to fail when copying artifacts.
ahoy cli "mkdir -p test/screenshots"

# Copy from the app container to the build host for storage.
mkdir -p /tmp/artifacts/behave
docker cp "$(docker-compose ps -q ckan)":/app/test/screenshots /tmp/artifacts/behave/
