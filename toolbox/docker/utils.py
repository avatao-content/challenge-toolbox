import os
import subprocess
from glob import glob
from typing import Any, Dict, Iterable, List, Tuple

from toolbox.config.docker import DOCKER_REGISTRY, DOCKER_REGISTRY_MIRRORS, WHITELISTED_DOCKER_REGISTRIES
from toolbox.utils import run_cmd, fatal_error


def get_image_url(image: str) -> str:
    for registry in WHITELISTED_DOCKER_REGISTRIES:
        if image.startswith(registry + '/'):
            return image
    if '/' not in image:
        return '/'.join((DOCKER_REGISTRY, image))

    fatal_error("Invalid image: %s registry not in whitelist: %s", image, str(WHITELISTED_DOCKER_REGISTRIES))


def get_challenge_image_url(
    repo_name: str, repo_branch: str, short_name: str, crp_config_item: Dict[str, Any]
) -> str:
    # Accept pre-set images which can only be relative in config.yml.
    image = crp_config_item.get('image')

    if not image:
        if repo_branch != 'master':
            tag = '-'.join((short_name, repo_branch))
        else:
            tag = short_name
        image = ':'.join((repo_name, tag))

    return get_image_url(image)


def pull_images(images: List[str], raise_errors=False):
    for image in images:
        run_cmd(['docker', 'pull', image], raise_errors=raise_errors)


def push_images(images: List[str]):
    for image in images:
        run_cmd(['docker', 'push', image])


def strip_image_registry(image: str) -> str:
    if '/' not in image:
        return image
    if image.startswith(DOCKER_REGISTRY + '/'):
        return image[len(DOCKER_REGISTRY) + 1:]

    fatal_error("Invalid image to strip: %s with registry: %s", image, DOCKER_REGISTRY)


def mirror_images(images: List[str]):
    for image in images:
        relative_image = strip_image_registry(image)
        for mirror in DOCKER_REGISTRY_MIRRORS:
            mirror_image = '/'.join((mirror, relative_image))
            try:
                run_cmd(['docker', 'tag', image, mirror_image])
                run_cmd(['docker', 'push', mirror_image])
            finally:
                run_cmd(['docker', 'rmi', mirror_image])


def yield_dockerfiles(
    repo_path: str, repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]
) -> Iterable[Tuple[str, str]]:

    for dockerfile in glob(os.path.join(repo_path, '*', 'Dockerfile')):
        short_name = os.path.basename(os.path.dirname(dockerfile))
        image = get_challenge_image_url(repo_name, repo_branch, short_name, crp_config[short_name])
        yield dockerfile, image


def sorted_container_configs(crp_config: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
    def sort_key(item: Tuple[str, Dict]):
        # The solvable must come first to share its volumes and namespaces
        if item[0] == "solvable":
            return 0
        # Then the controller if defined
        if item[0] == "controller":
            return 1
        # Then any other solvable in their current order
        return 2

    return sorted(crp_config.items(), key=sort_key)


def image_exists(image: str) -> bool:
    image_output: str = subprocess.check_output(['docker', 'images', '-q', image]).decode('utf-8').rstrip()
    if not image_output:
        return False
    return True