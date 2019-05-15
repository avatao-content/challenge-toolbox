from toolbox.docker.config import CRP_CONFIG_ABSOLUTE_IMAGE, DEPLOY_BRANCHES
from toolbox.docker.utils import get_image_url, yield_dockerfiles
from toolbox.utils import abort, run_cmd
from toolbox.utils.deploy import update_hook, upload_files


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    if repo_branch not in DEPLOY_BRANCHES:
        abort("Inactive branch: '%s' / %s", repo_branch, DEPLOY_BRANCHES)

    # Push absolute images URLs...
    for _, image in yield_dockerfiles(repo_path, repo_branch, repo_name):
        run_cmd(['docker', 'push', image])

    # ...but set relative image URLs for flexibility.
    for short_name, crp_config_item in config["crp_config"].items():
        crp_config_item["image"] = get_image_url(
            repo_name, repo_branch, short_name, absolute=CRP_CONFIG_ABSOLUTE_IMAGE)

    update_hook(repo_name, repo_branch, config)
    upload_files(repo_path, repo_name, repo_branch)
