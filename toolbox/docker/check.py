import json
import logging
import os
import re
import subprocess
from glob import glob as glob

from toolbox.utils import counted_error
from toolbox.utils.config import validate_bool, validate_flag, validate_ports
from toolbox.docker.utils import yield_dockerfiles
from toolbox.docker.config import *


def check_config(config: dict):
    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml: %s', invalid_keys)

    for item in config['crp_config'].values():
        if not isinstance(item, dict):
            counted_error('Items of crp_config must be dictionaries.')

        invalid_keys = set(item.keys()) - set(CRP_CONFIG_ITEM_KEYS)
        if invalid_keys:
            counted_error('Invalid key(s) found in crp_config: %s', invalid_keys)

        if 'image' in item and item['image'].find('/') > 0:
            counted_error('If the image is explicitly defined, it must be relative to the registry '
                          '- e.g. challenge:solvable.')

        if 'capabilities' in item:
            invalid_caps = set(item['capabilities']) - CAPABILITIES
            if len(invalid_caps) > 0:
                counted_error('Forbidden capabilities: %s\n\tAllowed capabilities: %s',
                              invalid_caps, CAPABILITIES)

        if 'kernel_params' in item:
            invalid_parameters = set(item['kernel_params']) - KERNEL_PARAMETERS
            if len(invalid_parameters) > 0:
                counted_error('Forbidden kernel parameters: %s\n\tAllowed parameters: %s',
                              invalid_parameters, KERNEL_PARAMETERS)

        if 'mem_limit_mb' in item:
            if not str(item['mem_limit_mb']).isnumeric() or not 4 < int(item['mem_limit_mb']) < 1024:
                counted_error('Invalid mem_limit_mb: %s. It should be an integer between 4 and 1024 MegaBytes.',
                              item['mem_limit_mb'])

        validate_bool('read_only', config.get('read_only', '0'))
        validate_ports(config['crp_config'].get('ports', []))

    validate_flag(config)


def check_dockerfile(filename):
    repo_pattern = 'FROM ((docker\.io\/)?avatao|eu\.gcr\.io\/avatao-challengestore)\/'
    try:
        with open(filename, 'r') as f:
            d = f.read()
            if re.search(repo_pattern, d) is None:
                counted_error('Please use avatao base images for your challenges. Our base images'
                              ' are available at https://hub.docker.com/u/avatao/')
    except FileNotFoundError as e:
        counted_error('Could not open %s', e.filename)

    except Exception as e:
        counted_error('An error occurred while loading %s. \n\tDetails: %s', filename, e)


def check_misc():
    if not len(glob('src/*')):
        logging.warning('Missing or empty "src" directory. Please place your source files there '
                        'if your challenge has any.')

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
    for dockerfile, image in yield_dockerfiles(repo_path, repo_name):
        check_dockerfile(dockerfile)
