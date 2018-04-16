#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; -*-
import logging
import subprocess
import sys
import time
import os

from common import get_sys_args, yield_dockerfiles
from common import run_cmd, init_logger


def build_image(repo_path, repo_name):
    for dockerfile, image in yield_dockerfiles(repo_path, repo_name):
        try:
            build_cmd = ['docker', 'build', '-t', image, '-f', dockerfile, repo_path]
            if os.environ.get('PULL_BASEIMAGES', '0') == '1':
                build_cmd.append('--pull')
            run_cmd(build_cmd)
        except subprocess.CalledProcessError:
            logging.error('Failed to build %s!' % dockerfile)
            sys.exit(1)

        time.sleep(1)


if __name__ == '__main__':
    """
    Build solvable and controller docker images from an avatao challenge repository.

    Simply add the challenge repository path as the first argument and the script does the rest.
    If a controller or solvable is missing, we skip it.

    After a successful build you can use the start.py to run your containers.
    """
    init_logger()
    build_image(*get_sys_args())
    logging.info('Finished. Everything is built.')
