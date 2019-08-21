import time

from toolbox.docker.config import PULL_BASEIMAGES
from toolbox.docker.utils import yield_dockerfiles
from toolbox.utils import abort_inactive_branch, run_cmd


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=True)

    for dockerfile, image in yield_dockerfiles(repo_path, repo_branch, repo_name):
        build_cmd = ['docker', 'build', '-t', image, '-f', dockerfile, repo_path]
        if PULL_BASEIMAGES:
            build_cmd.append('--pull')

        run_cmd(build_cmd)
        time.sleep(1)
