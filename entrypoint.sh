#!/bin/bash
# This script can be used as an entrypoint for build jobs
# or it can be "sourced" without parameters.
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
  if [ -n "${GOOGLE_APPLICATION_CREDENTIALS-}" ]; then
    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
  elif [ -n "${GOOGLE_SERVICE_ACCOUNT_KEY-}" ]; then
    gcloud auth activate-service-account --key-file=<(echo "$GOOGLE_SERVICE_ACCOUNT_KEY")
  fi

  if [ -n "${GOOGLE_PROJECT_ID-}" ]; then
    gcloud config set project "$GOOGLE_PROJECT_ID"
  fi
fi

# Ensure git submodules are up-to-date...
# This only makes sense if the current directory is the workspace.
if git rev-parse --git-dir &>/dev/null; then
  git submodule update --init --checkout --recursive
fi

# Log into docker registries from environment variables:
# DOCKER_LOGIN_[ID]_SERVER
# DOCKER_LOGIN_[ID]_USERNAME
# DOCKER_LOGIN_[ID]_PASSWORD
env \
  | grep -Po "^DOCKER_LOGIN_[\w_]+_(?=SERVER=)" \
  | xargs -r -I[] sh -c \
  'docker login -u "$[]USERNAME" -p "$[]PASSWORD" "$[]SERVER"'

# Execute the parameters...
if [ $# -ne 0 ]; then
  exec "$@"
fi
