import logging
import time
from typing import Optional

from toolbox.config.docker import PULL_BASEIMAGES
from toolbox.utils import abort_inactive_branch, parse_bool, run_cmd

from .utils import pull_images, yield_dockerfiles, yield_all_image_urls


def build_image(image: str, path: str, dockerfile: Optional[str] = None):
    build_cmd = ['docker', 'build', '-t', image]
    if dockerfile is not None:
        build_cmd += ['-f', dockerfile]

    if PULL_BASEIMAGES:
        build_cmd.append('--pull')

    build_cmd.append(path)
    run_cmd(build_cmd)

    # Let the engine cool off
    time.sleep(5)


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=True)

    if parse_bool(config.get('archive')):
        logging.warning('Skipping build. This challenge is archived.')
        return

    for dockerfile, image in yield_dockerfiles(repo_path, repo_name, repo_branch, config['crp_config']):
        build_image(image, repo_path, dockerfile)

    pull_images([
        image for _, image, is_built in yield_all_image_urls(repo_path, repo_name, repo_branch, config['crp_config'])
        if not is_built  # external images such as TFW
    ])
