#!/usr/bin/env bash
##
# Process test artifacts.
#
set -e

# Create screenshots directory in case it was not created before. This is to
# avoid this script to fail when copying artifacts.
ahoy cli "mkdir -p test/screenshots test/emails"

# Copy from the app container to the build host for storage.
mkdir -p /tmp/artifacts/behave
CONTAINER="$(docker-compose ps -q ckan)"
docker cp "$CONTAINER":test/screenshots /tmp/artifacts/behave/
docker cp "$CONTAINER":test/emails /tmp/artifacts/behave/
docker cp "$CONTAINER:mail/*" /tmp/artifacts/behave/emails/
