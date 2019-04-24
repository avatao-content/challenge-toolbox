import json
import logging
import os
import re
import subprocess
from glob import glob as glob

from toolbox.config import validate_bool, validate_flag, validate_ports
from toolbox.utils import counted_error


CONFIG_KEYS = {'version', 'crp_type', 'crp_config', 'flag', 'enable_flag_input'}

CRP_CONFIG_KEYS = {'source_image_project_id', 'source_image_family', 'ports', 'cpu_cores', 'mem_limit_gb', 'storage_limit_gb', 'nested'}


def check_config(config: dict):
    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml: %s', invalid_keys)

    if not isinstance(config.get('crp_config'), dict):
        counted_error('config.yml:crp_config must a dictionary.')

    invalid_keys = set(config['crp_config'].keys()) - set(CRP_CONFIG_KEYS)
    if invalid_keys:
        counted_error('Invalid key(s) found in config.yml:crp_config: %s', invalid_keys)

    if not config['crp_config'].get('source_image_family'):
        counted_error('Missing source_image_family - e.g. debian-9')

    try:
        cpu_cores = int(config['crp_config'].get('cpu_cores', 1))
        if cpu_cores < 1 or (cpu_cores > 1 and cpu_cores % 2 != 0) or cpu_cores > 64:
            raise ValueError
    except Exception:
        counted_error('Invalid cpu_cores value: %s. It must be 1 or an even number.',
                      config['crp_config'].get('cpu_cores'))

    else:
        if 'mem_limit_gb' in config['crp_config']:
            try:
                mem_limit_gb = float(config['crp_config']['mem_limit_gb'])
                if mem_limit_gb < 0.9 * cpu_cores or mem_limit_gb > 6.5 * cpu_cores or mem_limit_gb % 0.25 != 0:
                    raise ValueError
            except Exception:
                counted_error('Invalid mem_limit value: %s. It must be between 0.9 * cpu_cores and 6.5 * cpu_cores in 0.25 increments.',
                              config['crp_config'].get('mem_limit_gb'))

    if 'storage_limit_gb' in config['crp_config']:
        try:
            if not 10 <= int(config['crp_config']['storage_limit_gb']) <= 100:
                raise ValueError
        except Exception:
            counted_error('Invalid storage_limit_gb value: %s. It must be between 10 and 100 GigaBytes.',
                          config['crp_config'].get('storage_limit_gb'))

    validate_bool('nested', config['crp_config'].get('nested', '0'))
    validate_ports(config['crp_config'].get('ports', []))
    validate_flag(config)


def check_misc(repo_name: str):
    if re.match(r"^[a-z][a-z0-9-]{0,62}[a-z0-9]$", repo_name) is None:
        counted_error("Invalid repo name. Valid pattern: ^[a-z][a-z0-9-]{0,62}[a-z0-9]$")

    if not len(glob('setup.sh')):
        counted_error('Missing setup.sh file. Use it for what you would use a Dockerfile for.')

    if not len(glob('rootfs/*')):
        logging.warning('Missing or empty "rootfs" directory. Please place your source files there '
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
    check_misc(repo_name)
