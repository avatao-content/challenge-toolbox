import logging
import os
import re
from glob import glob

from toolbox.utils import check_common_files, counted_error, validate_bool, validate_flag, validate_ports

from .config import CONFIG_KEYS, CRP_CONFIG_ITEM_KEYS, CAPABILITIES, KERNEL_PARAMETERS
from .utils import yield_dockerfiles


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
            if invalid_caps > 0:
                counted_error('Forbidden capabilities: %s\n\tAllowed capabilities: %s',
                              invalid_caps, CAPABILITIES)

        if 'kernel_params' in item:
            invalid_parameters = set(item['kernel_params']) - KERNEL_PARAMETERS
            if invalid_parameters > 0:
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
    repo_pattern = r'FROM ((docker\.io\/)?avatao|eu\.gcr\.io\/avatao-challengestore)\/'
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
    check_common_files()

    if not glob('src/*'):
        logging.warning('Missing or empty "src" directory. Please place your source files there '
                        'if your challenge has any.')


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    os.chdir(repo_path)
    check_config(config)
    check_misc()
    for dockerfile, _ in yield_dockerfiles(repo_path, repo_branch, repo_name):
        check_dockerfile(dockerfile)
