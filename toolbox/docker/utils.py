import os
import posixpath
from glob import glob


DOCKER_REGISTRY = os.getenv('DOCKER_REGISTRY', 'eu.gcr.io/avatao-challengestore')


def get_image_url(repo_name: str, short_name: str=None, absolute: bool=True) -> str:
    """
    Return an absolute docker image URL

    :param repo_name: name of the docker repository (challenge name)
    :param short_name: [optional] e.g. solvable or controller
    :param absolute: [optional] return the absolute URL using the default registry?
    :return: absolute URL
    """
    if short_name is not None:
        repo_name = ':'.join((repo_name, short_name))

    if absolute:
        return posixpath.join(DOCKER_REGISTRY, repo_name)
    else:
        return repo_name


def yield_dockerfiles(repo_path: str, repo_name: str, absolute: bool=True):
    """
    Yield (Dockerfile, image_url) pairs from the given repo_path

    :param repo_path: the repo path (parent of config.yml)
    :param repo_name: name of the docker repository (challenge name)
    :param absolute: [optional] yield absolute image URLs using the default registry?
    """
    for dockerfile in glob(os.path.join(repo_path, '*', 'Dockerfile')):
        short_name = os.path.basename(os.path.dirname(dockerfile))
        image = get_image_url(repo_name, short_name, absolute)
        yield dockerfile, image
