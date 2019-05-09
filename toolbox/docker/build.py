import time

from toolbox.docker.config import BUILD_BRANCHES, PULL_BASEIMAGES
from toolbox.docker.utils import yield_dockerfiles
from toolbox.utils import abort, get_repo_branch, run_cmd

# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in BUILD_BRANCHES:
        abort("Inactive branch. Active branches: %s", BUILD_BRANCHES)

    for dockerfile, image in yield_dockerfiles(repo_path, repo_name):
        build_cmd = ['docker', 'build', '-t', image, '-f', dockerfile, repo_path]
        if PULL_BASEIMAGES:
            build_cmd.append('--pull')

        run_cmd(build_cmd)
        time.sleep(1)
