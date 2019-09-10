import logging
import json
import os
import shlex
import subprocess

from toolbox.utils import abort_inactive_branch, parse_bool, fatal_error

from .config import (
    AVATAO_USER,
    CONTROLLER_USER,
    GOOGLE_APPLICATION_CREDENTIALS,
    GOOGLE_PROJECT_ID,
    MIN_CPU_PLATFORM,
    PACKER_COMPUTE_ZONE,
    PACKER_PREEMPTIBLE,
    SSHD_CONFIG,
)


def _get_machine_type(config: dict) -> str:
    return f"custom-{config['crp_config']['cpu_cores']}-{int(config['crp_config']['mem_limit_gb'] * 1024)}"


def packer_builders(repo_name: str, repo_branch: str, config: dict) -> list:
    compute_builder = {
        'type': 'googlecompute',
        'project_id': GOOGLE_PROJECT_ID,
        'zone': PACKER_COMPUTE_ZONE,
        'machine_type': _get_machine_type(config),
        'disk_size': config['crp_config']['storage_limit_gb'],
        'image_name': '-'.join((repo_name, repo_branch)),
        'image_family': repo_name,
        'source_image_family': config['crp_config']['source_image_family'],
        'ssh_username': config['crp_config'].get('ssh_username', 'packer'),
        'communicator': 'ssh',
        'min_cpu_platform': MIN_CPU_PLATFORM,
        'preemptible': PACKER_PREEMPTIBLE,
    }

    if parse_bool(config.get('nested', '0')):
        compute_builder['image_licenses'] = ['projects/vm-options/global/licenses/enable-vmx']

    if GOOGLE_APPLICATION_CREDENTIALS:
        compute_builder['account_file'] = GOOGLE_APPLICATION_CREDENTIALS

    return [compute_builder]


def packer_provisioners(repo_path: str) -> list:
    provisioners = [
        {
            'type': 'shell',
            'inline': [
                'echo {} | sudo tee /etc/ssh/sshd_config >/dev/null'.format(shlex.quote(SSHD_CONFIG)),
                'sudo useradd -m -s /bin/bash {}'.format(AVATAO_USER),
                'sudo useradd -m -s /bin/bash -G google-sudoers {}'.format(CONTROLLER_USER),
            ],
        },
        {
            'type': 'file',
            'source': os.path.join(repo_path, 'rootfs'),
            'destination': '/var/tmp/rootfs',
        },
        {
            'type': 'shell',
            'inline': [
                'sudo cp -av --no-preserve=ownership /var/tmp/rootfs/* /',
                'sudo rm -rf /var/tmp/rootfs',
                'sudo chown -R {0}: /home/{0}'.format(AVATAO_USER),
                'sudo chown -R {0}: /home/{0}'.format(CONTROLLER_USER),
            ],
        },
        {
            'type': 'shell',
            'script': os.path.join(repo_path, 'setup.sh'),
        }
    ]
    return provisioners


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    abort_inactive_branch(repo_branch, allow_local=False)

    packer = json.dumps({
        'builders': packer_builders(repo_name, repo_branch, config),
        'provisioners': packer_provisioners(repo_path),
    })
    logging.debug(packer)

    proc = subprocess.Popen(['packer', 'build', '-force', '-'], cwd=repo_path, stdin=subprocess.PIPE)
    proc.communicate(packer.encode('utf-8'))
    if proc.wait() > 0:
        fatal_error('Failed to build GCE VM image!')
