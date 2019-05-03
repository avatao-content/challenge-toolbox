import logging
import json
import os
import subprocess
from datetime import datetime

from toolbox.config import parse_bool
from toolbox.utils import run_cmd


GOOGLE_PROJECT_ID = os.environ.get('GOOGLE_PROJECT_ID', 'avatao-crp-gce-dev-b16f85a6')
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
COMPUTE_ZONE = os.environ.get('CLOUDSDK_COMPUTE_ZONE', 'europe-west1-d')

AVATAO_USER = "user"
CONTROLLER_USER = "controller"

SSHD_CONFIG = """Port 22
AuthenticationMethods password publickey
PasswordAuthentication yes
UsePAM yes
UseDNS no
"""


def packer_builders(repo_name: str, config: dict) -> list:
    compute_builder = {
        'type': 'googlecompute',
        'project_id': GOOGLE_PROJECT_ID,
        'zone': COMPUTE_ZONE,
        'image_name': '{}-{}'.format(repo_name, datetime.now().strftime("%Y%d%m-%H%M%S")),
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
                'echo "{}" | sudo tee /etc/ssh/sshd_config >/dev/null'.format(SSHD_CONFIG.replace('\n', '\\n')),
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


# TODO: Allow JavaScript and Go.
def deploy_controller(repo_path: str, repo_name: str) -> list:
    controller_path = os.path.join(repo_path, 'controller')
    if os.path.isdir(controller_path):
        run_cmd(
            ['gcloud', 'functions', 'deploy', repo_name, '--entry-point=main', '--runtime=python37', '--trigger-http'],
            cwd=controller_path,
        )


def run(repo_path: str, repo_name: str, config: dict):
    # Do the controller first so if it fails we do not waste resources on the build.
    deploy_controller(repo_path, repo_name)

    packer = json.dumps({
        'builders': packer_builders(repo_name, config),
        'provisioners': packer_provisioners(repo_path),
    })
    logging.info(packer)
    proc = subprocess.Popen(['packer', 'build', '-'], cwd=repo_path, stdin=subprocess.PIPE)
    proc.communicate(packer.encode('utf-8'))
    proc.wait()
