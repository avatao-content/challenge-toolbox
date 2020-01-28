from toolbox.config.docker import ABSOLUTE_IMAGES
from toolbox.utils import abort_inactive_branch, run_cmd, update_hook, upload_files

from .utils import get_image_url, yield_dockerfiles


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)

    if not config['archive']:
        # Push absolute images URLs...
        for _, image in yield_dockerfiles(repo_path, repo_name, repo_branch):
            run_cmd(['docker', 'push', image])
        built_branch = repo_branch
    else:
        built_branch = 'master'

    # ...but set relative URLs by default for flexibility.
    for short_name, crp_config_item in config["crp_config"].items():
        crp_config_item["image"] = get_image_url(
            repo_name, built_branch, short_name, absolute=ABSOLUTE_IMAGES)

    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_path, repo_name, repo_branch, config)
