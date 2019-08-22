import logging
import json
import os
import shlex
import subprocess

from toolbox.utils import abort_inactive_branch, parse_bool

from .config import (
    AVATAO_USER,
    CONTROLLER_USER,
    GOOGLE_APPLICATION_CREDENTIALS,
    GOOGLE_PROJECT_ID,
    PACKER_COMPUTE_ZONE,
    SSHD_CONFIG,
)


def packer_builders(repo_name: str, repo_branch: str, config: dict) -> list:
    compute_builder = {
        'type': 'googlecompute',
        'project_id': GOOGLE_PROJECT_ID,
        'zone': PACKER_COMPUTE_ZONE,
        'image_name': '-'.join((repo_name, repo_branch)),
        'image_family': repo_name,
        'source_image_family': config['crp_config']['source_image_family'],
        # Use 1 VCPU 1.7 GB RAM for building. User instances can be any size.
        'machine_type': 'n1-standard-1',
        'min_cpu_platform': 'Intel Skylake',
        'disk_size': config['crp_config']['storage_limit_gb'],
        'ssh_username': config['crp_config'].get('ssh_username', 'packer'),
        'communicator': 'ssh',
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
                'sudo useradd -m {}'.format(AVATAO_USER),
                'sudo useradd -m -G google-sudoers {}'.format(CONTROLLER_USER),
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
                'sudo chown -R {0}: /home/{0}'.format(AVATAO_USER),
                'sudo chown -R {0}: /home/{0}'.format(CONTROLLER_USER),
                'sudo rm -rf /var/tmp/rootfs',
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
    proc.wait()