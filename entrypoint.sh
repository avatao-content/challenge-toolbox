#!/bin/bash
set -aeuo pipefail

git submodule update --init --checkout --recursive --remote

if [ -n "${DRONE_SYSTEM_HOSTNAME-}" ]; then
  source "/etc/docker/avatao-challenge-toolbox/${DRONE_SYSTEM_HOSTNAME}"
elif [ -e "$(dirname "$0")/.env" ]; then
  source "$(dirname "$0")/.env"
elif [ -e "./.env" ]; then
  source "./.env"
fi

if [ -n "${GOOGLE_APPLICATION_CREDENTIALS-}" ]; then
  gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
fi

if [ -n "${PROJECT_ID-}" ] && [ -n "${BUILD_ID-}" ]; then # Google Cloud Build
  export GOOGLE_PROJECT_ID="$PROJECT_ID"
  export CI=true
fi

if [ -n "${GOOGLE_PROJECT_ID-}" ]; then
  gcloud config set project "$GOOGLE_PROJECT_ID"
fi

exec "$@"
