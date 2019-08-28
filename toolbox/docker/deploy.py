from toolbox.utils import abort_inactive_branch, run_cmd, update_hook, upload_files

from .config import CRP_CONFIG_ABSOLUTE_IMAGE
from .utils import get_image_url, yield_dockerfiles


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)

    # Push absolute images URLs...
    for _, image in yield_dockerfiles(repo_path, repo_name, repo_branch):
        run_cmd(['docker', 'push', image])

    # ...but set relative URLs by default for flexibility.
    for short_name, crp_config_item in config["crp_config"].items():
        crp_config_item["image"] = get_image_url(
            repo_name, repo_branch, short_name, absolute=CRP_CONFIG_ABSOLUTE_IMAGE)

    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_name, repo_branch, config)
