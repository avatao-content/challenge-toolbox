import logging
import sys

from toolbox.utils import fatal_error


def run(repo_path: str, repo_name: str, config: dict):
    fatal_error('Local VM start is not yet implemented.\n\tPlease, use a %s VM for development.',
                config['crp_config'].get('source_image_family', 'debian'))
