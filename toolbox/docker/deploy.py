import json
import logging
import os
from subprocess import check_output

from toolbox.config.docker import ABSOLUTE_IMAGES
from toolbox.utils import abort_inactive_branch, fatal_error, run_cmd, update_hook, upload_files

from .utils import get_image_url, sorted_container_configs, yield_dockerfiles
from .start import start_containers, remove_containers


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)
    os.chdir(repo_path)

    if not config.get('archive'):
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

    try:
        # Get the first container's name (and process) then inspect its volumes.
        # By running the containers, we also check whether the challenge can be started.
        volumes_list = []
        for container_name, _ in start_containers(repo_name, repo_branch, config).items():
            volumes_json = check_output(['docker', 'inspect', '-f', '{{json .Config.Volumes}}', container_name])
            volumes_list = list(json.loads(volumes_json).keys())
            print(volumes_list)
            break

        if volumes_list:
            # Store the volumes in the first container's crp_config item.
            for _, crp_config_item in sorted_container_configs(config["crp_config"]):
                if "volumes" not in crp_config_item:
                    crp_config_item["volumes"] = volumes_list
                    logging.debug("Automatically set shared volumes: %s", volumes_list)
                else:
                    logging.debug("Ignoring inspected volumes: %s", volumes_list)
                break

    except Exception as e:
        logging.exception(e)
        fatal_error("Failed to run or inspect containers!")

    finally:
        remove_containers()

    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_path, repo_name, repo_branch, config)
