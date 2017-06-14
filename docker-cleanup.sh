#!/usr/bin/env bash
# POSIX compatible interactive docker cleanup script

echo -n 'Delete ALL containers (y/N)? ' >&2
read answer

if echo "$answer" | grep -iq "^Y" ; then
  ids="$(docker ps -qa)"
  test -n "$ids" && echo "$ids" | xargs docker rm -fv
fi

echo -n 'Delete dangling volumes (y/N)? ' >&2
read answer

if echo "$answer" | grep -iq "^Y" ; then
  ids="$(docker volume ls -qf dangling=true)"
  test -n "$ids" && echo "$ids" | xargs docker volume rm
fi

echo -n 'Delete dangling images (y/N)? ' >&2
read answer

if echo "$answer" | grep -iq "^Y" ; then
  ids="$(docker images -qf dangling=true)"
  test -n "$ids" && echo "$ids" | xargs docker rmi
fi
