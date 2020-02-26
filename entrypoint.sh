#!/bin/bash
set -aeuo pipefail

env | grep ^DRONE | grep -Ev "PASSWORD|SECRET|TOKEN" >&2
git submodule update --init --checkout --recursive --remote

if [ -n "${DRONE_SYSTEM_HOSTNAME-}" ]; then
  source "/etc/docker/avatao-challenge-toolbox/${DRONE_SYSTEM_HOSTNAME}"
else
  echo "# DRONE_SYSTEM_HOSTNAME is unset. Falling back to .env" >&2
  source "$(dirname "$0")/.env"
fi

if [ -n "${GOOGLE_APPLICATION_CREDENTIALS-}" ]; then
  gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
fi

if [ -n "${GOOGLE_PROJECT_ID-}" ]; then
  gcloud config set project "$GOOGLE_PROJECT_ID"
fi

exec "$@"
