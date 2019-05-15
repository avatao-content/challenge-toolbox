from toolbox.static.config import DEPLOY_BRANCHES
from toolbox.utils import abort
from toolbox.utils.deploy import update_hook, upload_files


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    if repo_branch not in DEPLOY_BRANCHES:
        abort("Inactive branch: '%s' / %s", repo_branch, DEPLOY_BRANCHES)

    update_hook(repo_name, repo_branch, config)
    upload_files(repo_path, repo_name, repo_branch)
