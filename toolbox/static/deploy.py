from toolbox.utils import abort, get_repo_branch, run_cmd
from toolbox.utils.deploy import update_hook
from toolbox.docker.utils import yield_dockerfiles
from toolbox.docker.config import *


def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in ACTIVE_BRANCHES:
        abort("Inactive branch. Active branches: %s", ACTIVE_BRANCHES)

    update_hook(repo_name, config)
