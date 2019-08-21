from toolbox.utils import abort_inactive_branch
from toolbox.utils.deploy import update_hook, upload_files


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)
    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_name, repo_branch, config)
