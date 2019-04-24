import json
import logging
import os
import re
import subprocess
from glob import glob

from toolbox.config import validate_flag
from toolbox.utils import counted_error


CONFIG_KEYS = {'version', 'flag', 'enable_flag_input'}


def check_config(config: dict):
    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml: %s', invalid_keys)

    validate_flag(config, flag_required=True)


def check_misc():
    if not len(glob('src/*')):
        logging.warning('Missing or empty "src" directory. Please place your source files there '
                        'if your challenge has any.')

    if not len(glob('downloads/*')):
        logging.warning('Static challenges should have a "downloads" directory for sharing challenge files with users.')

    if not len(glob('README.md')):
        logging.warning('No README.md file is found. Readmes help others to understand your challenge.')

    if not len(glob('LICENSE')):
        logging.warning('No LICENSE file is found. Please add the (original) license file if you copied'
                        '\n\t  a part of your challenge from a licensed challenge.')

    if not len(glob('CHANGELOG')):
        logging.warning('No CHANGELOG file is found. If you modified an existing licensed challenge,\n\t'
                        'please, summarize what your changes were.')

    if not len(glob('.drone.yml')):
        logging.warning('No .drone.yml file is found. This file is necessary for our automated tests,\n\t'
                        'please, get it from any template before uploading your challenge.')


def run(repo_path: str, repo_name: str, config: dict):
    os.chdir(repo_path)
    check_config(config)
    check_misc()
