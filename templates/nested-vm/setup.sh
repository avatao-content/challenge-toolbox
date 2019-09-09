#!/bin/bash
set -euo pipefail

if [ $UID -ne 0 ]; then
    # Reexec as root
    exec sudo "$0" "$@"
fi

# Allow root privileges for the challenge user
#usermod -a -G google-sudoers user

# I don't like your aptitude, boy!
apt-get update
apt-get install -qy apt-transport-https

echo "Challenge setup goes here!"
