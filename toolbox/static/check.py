import logging
import os
from glob import glob

from toolbox.utils import check_common_files, counted_error, validate_flag

from .config import CONFIG_KEYS


def check_config(config: dict):
    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml: %s', invalid_keys)

    validate_flag(config, flag_required=True)


def check_misc():
    check_common_files()

    if not glob('src/*'):
        logging.warning('Missing or empty "src" directory. Please place your source files there '
                        'if your challenge has any.')

    if not glob('downloads/*'):
        logging.warning('Static challenges should have a "downloads" directory for sharing challenge files with users.')


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    os.chdir(repo_path)
    check_config(config)
    check_misc()
