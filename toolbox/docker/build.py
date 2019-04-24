import logging
import os
import subprocess
import sys
import time

from toolbox.utils import run_cmd
from toolbox.docker.utils import yield_dockerfiles


PULL_BASEIMAGES = os.environ.get('TOOLBOX_PULL_BASEIMAGES', '0').lower() in ('true', '1')


def run(repo_path: str, repo_name: str, config: dict):
    for dockerfile, image in yield_dockerfiles(repo_path, repo_name):
        try:
            build_cmd = ['docker', 'build', '-t', image, '-f', dockerfile, repo_path]
            if PULL_BASEIMAGES:
                build_cmd.append('--pull')

            run_cmd(build_cmd)
            time.sleep(1)

        except subprocess.CalledProcessError:
            logging.error('Failed to build %s!' % dockerfile)
            sys.exit(1)
