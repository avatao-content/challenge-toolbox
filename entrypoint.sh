#!/bin/sh
# This script can be used as an entrypoint for build jobs
# or it can be "sourced" without parameters. Supports POSIX shells.
set -aeuo pipefail

if [ -e "$(dirname "$0")/.env" ]; then
  source "$(dirname "$0")/.env"
fi

if [ -e ".env" ]; then
  source ".env"
fi

# Support Google Cloud Build
if [ -n "${PROJECT_ID-}" ] && [ -n "${BUILD_ID-}" ]; then
  export GOOGLE_PROJECT_ID="$PROJECT_ID"
  export CI=true
fi

# Configure Google Cloud SDK
if command -v gcloud &>/dev/null; then
  if [ -n "${GOOGLE_SERVICE_ACCOUNT_KEY-}" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="/tmp/challenge-toolbox-google-service-account-key.json"
    echo "$GOOGLE_SERVICE_ACCOUNT_KEY" > "$GOOGLE_APPLICATION_CREDENTIALS"
  fi

  if [ -n "${GOOGLE_APPLICATION_CREDENTIALS-}" ]; then
    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
  fi

  if [ -n "${GOOGLE_PROJECT_ID-}" ]; then
    gcloud config set project "$GOOGLE_PROJECT_ID"
  fi
fi

# Log into docker registries from environment variables:
# DOCKER_LOGIN_[ID]_{SERVER,USERNAME,PASSWORD}
env | grep -Eo "^DOCKER_LOGIN_[A-Z0-9_]+_" | sort -u | xargs -r -I[] sh -c \
  'echo "$[]PASSWORD" | docker login --username "$[]USERNAME" "$[]SERVER"  --password-stdin '

# Execute the parameters...
if [ $# -ne 0 ]; then
  exec "$@"
fi
