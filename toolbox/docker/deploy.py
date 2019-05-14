from toolbox.docker.config import DEPLOY_BRANCHES
from toolbox.docker.utils import yield_dockerfiles
from toolbox.utils import abort, get_repo_branch, run_cmd
from toolbox.utils.deploy import update_hook, upload_files


def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in DEPLOY_BRANCHES:
        abort("Inactive branch. Active branches: %s", DEPLOY_BRANCHES)

    for _, image in yield_dockerfiles(repo_path, repo_name):
        run_cmd(['docker', 'push', image])

    update_hook(repo_name, config)
    upload_files(repo_path)
