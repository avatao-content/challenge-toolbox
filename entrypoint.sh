#!/bin/bash
set -aeuo pipefail

if [ -n "${CI_SYSTEM_LINK-}" ]; then
  source "/etc/docker/avatao-challenge-toolbox/${CI_SYSTEM_LINK}"
else
  echo "# CI_SYSTEM_LINK is unset. Falling back to .env" >&2
  source "$(dirname "$0")/.env"
fi

if [ -n "${GOOGLE_APPLICATION_CREDENTIALS-}" ]; then
  gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
fi

if [ -n "${GOOGLE_PROJECT_ID-}" ]; then
  gcloud config set project "$GOOGLE_PROJECT_ID"
fi

env | grep ^DRONE >&2
exec "$@"
