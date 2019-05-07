import logging
import os
import subprocess
import sys
import time

from toolbox.utils import fatal_error, run_cmd
from toolbox.docker.utils import yield_dockerfiles
from toolbox.docker.config import *


def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in ACTIVE_BRANCHES:
        abort("Inactive branch. Active branches: %s", ACTIVE_BRANCHES)

    for dockerfile, image in yield_dockerfiles(repo_path, repo_name):
        try:
            build_cmd = ['docker', 'build', '-t', image, '-f', dockerfile, repo_path]
            if PULL_BASEIMAGES:
                build_cmd.append('--pull')

            run_cmd(build_cmd)
            time.sleep(1)

        except subprocess.CalledProcessError:
            fatal_error('Failed to build %s!', dockerfile)
