import logging
import os
import re
from glob import glob

from toolbox.config.docker import CONFIG_KEYS, CRP_CONFIG_ITEM_KEYS, CAPABILITIES
from toolbox.utils import check_common_files, counted_error, validate_bool, validate_flag, validate_ports

from .utils import sorted_container_configs, yield_dockerfiles


def check_config(config: dict):  # pylint: disable=too-many-branches
    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml: %s', invalid_keys)

    first = True
    for _, item in sorted_container_configs(config['crp_config']):
        if not isinstance(item, dict):
            counted_error('Items of crp_config must be dictionaries.')

        invalid_keys = set(item.keys()) - set(CRP_CONFIG_ITEM_KEYS)
        if invalid_keys:
            counted_error('Invalid key(s) found in crp_config: %s', invalid_keys)

        if 'capabilities' in item:
            invalid_caps = set(item['capabilities']) - CAPABILITIES
            if invalid_caps:
                counted_error('Forbidden capabilities: %s\n\tAllowed capabilities: %s',
                              invalid_caps, CAPABILITIES)

        if 'mem_limit_mb' in item:
            if not str(item['mem_limit_mb']).isnumeric() or not 8 <= int(item['mem_limit_mb']) <= 4096:
                counted_error('Invalid mem_limit_mb: %s. It should be an integer between 8 and 2048 MegaBytes.',
                              item['mem_limit_mb'])

        if 'cpu_limit_ms' in item:
            if not str(item['cpu_limit_ms']).isnumeric() or not 100 <= int(item['cpu_limit_ms']) <= 4000:
                counted_error('Invalid cpu_limit_ms: %s. It should be an integer between 100 and 4000 CPU milliseconds.',
                              item['cpu_limit_ms'])

        if 'volumes' in item:
            if not first:
                counted_error('Only the first container [solvable, controller, ...] can set shared volumes.')
            else:
                logging.warning('Shared volumes are manually set. Is this what you want?')

        validate_bool('read_only', item.get('read_only', '0'))
        validate_ports(item.get('ports', []), item.get('buttons', None))
        first = False

    validate_flag(config)


def check_dockerfile(filename):
    repo_pattern = r'FROM ((docker\.io\/)?avatao|eu\.gcr\.io\/avatao-challengestore)\/'
    try:
        with open(filename, 'r') as f:
            d = f.read()
            if re.search(repo_pattern, d) is None:
                counted_error('Please, use avatao base images for your challenges. Our base images '
                              'are available at https://hub.docker.com/u/avatao/')
    except FileNotFoundError as e:
        counted_error('Could not open %s', e.filename)

    except Exception as e:
        counted_error('An error occurred while loading %s. \n\tDetails: %s', filename, e)


def check_misc():
    check_common_files()

    if not glob('src/*'):
        logging.warning('Missing or empty "src" directory. Please, place your source files there '
                        'if your challenge has any.')


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    os.chdir(repo_path)

    check_config(config)
    check_misc()

    for dockerfile, _ in yield_dockerfiles(repo_path, repo_branch, repo_name, config['crp_config']):
        check_dockerfile(dockerfile)
