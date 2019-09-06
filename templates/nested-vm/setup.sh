#!/bin/bash
set -euo pipefail

if [ $UID -ne 0 ]; then
    # Reexec as root
    exec sudo "$0" "$@"
fi

echo "Setup goes here!"
