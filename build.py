#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; -*-

import logging
import os
import posixpath
import subprocess
import sys
import time
import re

_docker_repo_name = os.getenv('CI_BUILD_REPO', '/avatao/').split('/')[-2]
DOCKER_REPO = os.getenv('DOCKER_REPOSITORY', _docker_repo_name)
DOCKER_REGISTRY_URL = re.sub('\/$', '', os.getenv('DOCKER_REGISTRY_URL', '').replace('https://',''))

def _set_logger():

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('\n[%(levelname)s] %(message)s\n')
    ch.setFormatter(formatter)
    root.addHandler(ch)

def _run_cmd(cargs):
    logging.info("Running %s", cargs)
    return subprocess.Popen(cargs)


def _build_image(repo_path):

    repo_path = os.path.realpath(repo_path)

    # If you do not want to build both images, just simply modify the
    # name of image (e.g., 'solvable_') you do not need and the script skips it.
    for image_type in ('solvable', 'controller'):

        dockerfile = os.path.join(repo_path, image_type, 'Dockerfile')

        if not os.path.exists(dockerfile):
            logging.warning('Could not find %s. Skipping...' % image_type)
            continue

        repo_name = os.path.basename(repo_path)
        image = posixpath.join(DOCKER_REPO, '%s-%s' % (repo_name, image_type))

        logging.info('Trying to build %s ...' % image)

        try:
            _run_cmd(['docker', 'build', '-t', image, '-f', dockerfile, repo_path]).wait()
        except subprocess.CalledProcessError:
            logging.error('Failed to build %s. Please make sure that your Dockerfile is correct.' % image_type)
            sys.exit(1)

        time.sleep(1)


if __name__ == '__main__':

    """
    Build solvable and controller docker images from an avatao challenge repository.

    Simply add the challenge repository path as the first argument and the script does the rest.
    If a controller or solvable is missing, we skip it.

    After a successful build you can use the start.py to run your containers.
    """

    _set_logger()

    if len(sys.argv) != 2:
        logging.info('Usage: ./build.py <repository_path>')
        sys.exit(1)

    _build_image(sys.argv[1])

    logging.info('Finished. Everything is built.')
