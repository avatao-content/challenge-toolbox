import re
import os
from glob import glob
from typing import Any, Dict, Iterable, List, Tuple

from toolbox.config.docker import DOCKER_REGISTRY, DOCKER_REGISTRY_MIRRORS
from toolbox.utils import run_cmd

IMAGE_RE = re.compile(rf'^(?:{re.escape(DOCKER_REGISTRY)}/)?(.+)$')


def get_image_url(repo_name: str, repo_branch: str, short_name: str, crp_config_item: Dict[str, Any]) -> str:
    # Accept pre-set images which can only be relative in config.yml or set by us.
    image = crp_config_item.get('image')

    if not image:
        if repo_branch != 'master':
            tag = '-'.join((short_name, repo_branch))
        else:
            tag = short_name
        image = ':'.join((repo_name, tag))

    if not image.startswith(DOCKER_REGISTRY):
        return '/'.join((DOCKER_REGISTRY, image))

    return image


def pull_images(images: List[str]):
    for image in images:
        run_cmd(['docker', 'pull', image])


def push_images(images: List[str]):
    for image in images:
        run_cmd(['docker', 'push', image])


def mirror_images(images: List[str]):
    for image in images:
        for mirror in DOCKER_REGISTRY_MIRRORS:
            mirror_image = '/'.join((mirror, IMAGE_RE.match(image).group(1)))
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
        image = get_image_url(repo_name, repo_branch, short_name, crp_config[short_name])
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
