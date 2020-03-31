import os
from glob import glob
from typing import Dict, Iterable, List, Tuple

from toolbox.config.docker import DOCKER_REGISTRY


def get_image_url(repo_name: str, repo_branch: str, crp_config: Dict[str, Dict], short_name: str) -> str:
    """
    Return an absolute docker image URL

    :param repo_name: name of the docker repository (challenge name)
    :param repo_branch: branch of the git repo (challenge version)
    :param short_name: [optional] e.g. solvable or controller
    :param crp_config: config['crp_config']
    :return: absolute URL
    """
    image = crp_config[short_name].get('image')

    if not image:
        if repo_branch != 'master':
            tag = '-'.join((short_name, repo_branch))
        else:
            tag = short_name
        image = ':'.join((repo_name, tag))

    if not image.startswith(DOCKER_REGISTRY):
        return '/'.join((DOCKER_REGISTRY, image))

    return image


def yield_dockerfiles(repo_path: str, repo_name: str, repo_branch: str, config: dict) -> Iterable[Tuple[str, str]]:
    """
    Yield (Dockerfile, image_url) pairs from the given repo_path

    :param repo_path: the repo path (parent of config.yml)
    :param repo_name: name of the docker repository (challenge name)
    :param config: parsed config.yml
    """
    for dockerfile in glob(os.path.join(repo_path, '*', 'Dockerfile')):
        short_name = os.path.basename(os.path.dirname(dockerfile))
        image = get_image_url(repo_name, repo_branch, config['crp_config'], short_name)
        yield dockerfile, image


def sorted_container_configs(containers: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
    def sort_key(item: Tuple[str, Dict]):
        # The solvable must come first to share its volumes and namespaces
        if item[0] == "solvable":
            return 0
        # Then the controller if defined
        if item[0] == "controller":
            return 1
        # Then any other solvable in their current order
        return 2

    return sorted(containers.items(), key=sort_key)
