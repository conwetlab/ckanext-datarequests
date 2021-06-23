#!/usr/bin/env bash
##
# Run tests in CI.
#
set -e

echo "==> Lint code"
ahoy lint

echo "==> Run Unit tests"
ahoy test-unit

echo "==> Run BDD tests"
ahoy test-bdd || (ahoy cli 'find / -type d -name "*mail*"'; ahoy logs; exit 1)
