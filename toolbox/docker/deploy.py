import json
import logging
import os
from typing import Dict, List, Tuple

from toolbox.config.docker import ARCHIVE_BRANCH
from toolbox.utils import abort_inactive_branch, fatal_error, parse_bool, run_cmd, update_hook, upload_files

from .utils import mirror_images, pull_images, push_images, sorted_container_configs, yield_all_image_urls
from .start import start_containers, remove_containers


def set_image_urls(
    repo_path, repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]
) -> Tuple[List[str], List[str]]:

    built_images = []
    external_images = []
    for short_name, image, is_built in yield_all_image_urls(repo_path, repo_name, repo_branch, crp_config):
        crp_config[short_name]['image'] = image
        (built_images if is_built else external_images).append(image)
    return built_images, external_images


def start_and_set_volumes(repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]):
    # By running the containers, we also test whether the challenge can be started.
    try:
        # Get the first container's name (and process) then inspect its volumes.
        volumes_list = []
        for container_name, _ in start_containers(repo_name, repo_branch, crp_config).items():
            volumes_json: bytes = run_cmd(
                ['docker', 'inspect', '-f', '{{json .Config.Volumes}}', container_name],
                check_output=True)
            volumes_list = list(json.loads(volumes_json).keys())
            break

        if volumes_list:
            # Store the volumes in the first container's crp_config item.
            for _, crp_config_item in sorted_container_configs(crp_config):
                if 'volumes' not in crp_config_item:
                    crp_config_item['volumes'] = volumes_list
                    logging.debug('Automatically set shared volumes: %s', volumes_list)
                else:
                    logging.debug('Ignoring inspected volumes: %s', volumes_list)
                break

    except Exception as e:
        logging.exception(e)
        # sys.exit raises SystemExit in Python which will be re-raised after the finally block.
        fatal_error("Failed to run or inspect containers!")

    finally:
        remove_containers()


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)
    is_archived = parse_bool(config.get('archive'))
    built_branch = ARCHIVE_BRANCH if is_archived else repo_branch
    os.chdir(repo_path)

    built_images, external_images = set_image_urls(repo_path, repo_name, built_branch, config['crp_config'])

    if is_archived:
        pull_images(built_images + external_images)

    start_and_set_volumes(repo_name, built_branch, config['crp_config'])

    if not is_archived:
        push_images(built_images)

    mirror_images(built_images)
    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_path, repo_name, repo_branch, config)
