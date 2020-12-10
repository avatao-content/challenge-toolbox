#!/usr/bin/env python3
import logging
from os.path import join
import shutil
import os
import yaml
from glob import glob

from toolbox.utils import (
    CURRENT_MAX_VERSION,
    compare_version,
    abort,
    counted_error_at_exit,
    fatal_error,
    get_sys_args,
    init_logger,
    read_config,
    run_cmd,
)

TOOLBOX_PATH = os.path.dirname(__file__)


def upgrade_v2_0_to_v3_0(repo_path: str, config: dict):
    config['version'] = 'v3.0'

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
    run_cmd(['git', 'commit', '-q', '-m', 'Upgrade to spec v3', '.drone.yml', 'config.yml', 'metadata'], cwd=repo_path)
    logging.info('Challenge metadata needs to be migrated to the new platform!')


def upgrade_v3_0_to_v3_1(repo_path: str, config: dict):
    config['version'] = 'v3.1'

    with open(os.path.join(repo_path, 'config.yml'), 'w') as f:
        yaml.safe_dump(config, f)

    run_cmd(['rm', '-rf', '.drone.yml', '.circleci'], cwd=repo_path)
    run_cmd(['cp', '-a', 'skeleton/.circleci', repo_path], cwd=TOOLBOX_PATH)
    run_cmd(['git', 'add', '.circleci'], cwd=repo_path)

    run_cmd(['git', 'commit', '-q', '-m', 'Upgrade to spec v3.1', '.drone.yml', '.circleci', 'config.yml'], cwd=repo_path)


def upgrade_v3_1_to_v3_2(repo_path: str, config: dict):
    config['version'] = 'v3.2'

    with open(os.path.join(repo_path, 'config.yml'), 'w') as f:
        yaml.safe_dump(config, f)

    run_cmd(['git', 'commit', '-q', '-m', 'Upgrade to spec v3.2', 'config.yml'], cwd=repo_path)


# pylint: disable=unused-argument
def run(repo_path: str, repo_name: str, repo_branch: str):
    config = read_config(repo_path, pre_validate=False)
    upgraded = False

    # Abort if >= CURRENT_MAX_VERSION - ignore MIN version to force the latest version.
    if compare_version(config, CURRENT_MAX_VERSION, CURRENT_MAX_VERSION) >= 0:
        abort('Nothing to do.')

    if compare_version(config, 'v2.0', 'v2.0') == 0:
        upgrade_v2_0_to_v3_0(repo_path, config)
        upgraded = True

    if compare_version(config, 'v3.0', 'v3.0') == 0:
        upgrade_v3_0_to_v3_1(repo_path, config)
        upgraded = True

    if compare_version(config, 'v3.1', 'v3.1') == 0:
        upgrade_v3_1_to_v3_2(repo_path, config)
        upgraded = True

    if not upgraded:
        fatal_error('Unknown version!')

    logging.info('Run git push when you are ready.')


if __name__ == '__main__':
    init_logger()
    run(*get_sys_args())
    counted_error_at_exit()
