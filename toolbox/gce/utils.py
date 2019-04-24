import os
import posixpath
from glob import glob


def get_image_url(repo_name: str, short_name: str=None, absolute: bool=True) -> str:
    """
    Return an absolute docker image URL

    :param repo_name: name of the docker repository (challenge name)
    :param short_name: [optional] e.g. solvable or controller
    :param absolute: [optional] return the absolute URL using the default registry?
    :return: absolute URL
    """
    pass
