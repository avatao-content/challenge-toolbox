import logging
import json
import os
import subprocess

from toolbox.config import parse_bool
from toolbox.docker.utils import yield_dockerfiles


GOOGLE_PROJECT_ID = os.environ.get('GOOGLE_PROJECT_ID', 'avatao-crp-gce-dev-b16f85a6')

COMPUTE_ZONE = os.environ.get('CLOUDSDK_COMPUTE_ZONE', 'europe-west1-d')

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')


def packer_builders(repo_name: str, config: dict) -> list:
    compute_builder = {
        'type': 'googlecompute',
        'project_id': GOOGLE_PROJECT_ID,
        'zone': COMPUTE_ZONE,
        'image_family': repo_name,
        'source_image_family': config['crp_config']['source_image_family'],
        # Use 1 VCPU 1.7 GB RAM for building. User instances can be any size.
        'machine_type': 'n1-standard-1',
        'min_cpu_platform': 'Intel Haswell',
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
            'type': 'file',
            'source': os.path.join(repo_path, 'rootfs'),
            'destination': '/var/tmp/rootfs',
        },
        {
            'type': 'shell',
            'inline': [
                'sudo chown -R root:root /var/tmp/rootfs',
                'sudo mv /var/tmp/rootfs/* /',
                'sudo rmdir /var/tmp/rootfs',
            ],
        },
        {
            'type': 'shell',
            'script': os.path.join(repo_path, 'setup.sh'),
        }
    ]
    return provisioners


def run(repo_path: str, repo_name: str, config: dict):
    packer = json.dumps({
        'builders': packer_builders(repo_name, config),
        'provisioners': packer_provisioners(repo_path),
    })
    logging.info(packer)
    proc = subprocess.Popen(['packer', 'build', '-'], cwd=repo_path, stdin=subprocess.PIPE)
    proc.communicate(packer.encode('utf-8'))
    proc.wait()
