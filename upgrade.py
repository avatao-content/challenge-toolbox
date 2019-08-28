#!/usr/bin/env python3
import logging
import shutil
import subprocess
import os
import yaml
from glob import glob

from toolbox.utils import (
    CURRENT_MIN_VERSION,
    CURRENT_MAX_VERSION,
    compare_version,
    abort,
    counted_error_at_exit,
    get_sys_args,
    init_logger,
    read_config,
)


def upgrade_v2_to_v3(repo_path: str, config: dict):
    cmp = compare_version(config, 'v2', 'v2.999')
    if cmp < 0:
        abort('Unknown legacy version!')
    if cmp > 0:
        abort('Unknown future version!')

    config['version'] = 'v3'

    # There were only docker and static type of challenges in v2
    if glob(os.path.join(repo_path, '*', 'Dockerfile')):
        config['crp_type'] = 'docker'

        for item in config['crp_config'].values():
            if 'mem_limit' in item:
                item['mem_limit_mb'] = int(str(item['mem_limit']).rstrip('MBmb'))
                del item['mem_limit']

    # Obsolete config keys
    for key in ('type', 'name', 'difficulty', 'skills', 'recommendations', 'owners'):
        if key in config:
            del config[key]

    with open(os.path.join(repo_path, 'config.yml'), 'w') as f:
        f.write('---\n# Upgraded from v2\n')
        yaml.safe_dump(config, f)

    drone_config = yaml.safe_load(open(os.path.join(repo_path, '.drone.yml'), 'r'))
    drone_config['pipeline']['build']['image'] = 'eu.gcr.io/avatao-challengestore/challenge-builder:v3'

    with open(os.path.join(repo_path, '.drone.yml'), 'w') as f:
        f.write('---\n# Do not modify this file or your builds will be automatically rejected!\n')
        yaml.safe_dump(drone_config, f)

    shutil.rmtree(os.path.join(repo_path, 'metadata'))
    subprocess.check_call(['git', 'commit', '-q', '-m', 'Upgrade to spec v3', '.drone.yml', 'config.yml', 'metadata'], cwd=repo_path)

    logging.info('Challenge metadata needs to be migrated to the new platform!')
    logging.info('Run git push when you are ready.')


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str):
    config = read_config(repo_path, pre_validate=False)

    if compare_version(config, CURRENT_MIN_VERSION, CURRENT_MAX_VERSION) >= 0:
        abort('Nothing to do.')

    upgrade_v2_to_v3(repo_path, config)


if __name__ == '__main__':
    init_logger()
    run(*get_sys_args())
    counted_error_at_exit()
