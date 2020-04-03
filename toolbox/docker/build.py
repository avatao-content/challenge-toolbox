import logging
import time

from toolbox.config.docker import PULL_BASEIMAGES
from toolbox.utils import abort_inactive_branch, parse_bool, run_cmd

from .utils import yield_dockerfiles


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=True)

    if parse_bool(config.get('archive')):
        logging.warning('Skipping build. This challenge is archived.')
        return

    for dockerfile, image in yield_dockerfiles(repo_path, repo_name, repo_branch, config['crp_config']):
        build_cmd = ['docker', 'build', '-f', dockerfile, '-t', image]
        if PULL_BASEIMAGES:
            build_cmd.append('--pull')

        build_cmd.append(repo_path)
        run_cmd(build_cmd)

        # Let the engine cool off
        time.sleep(5)
