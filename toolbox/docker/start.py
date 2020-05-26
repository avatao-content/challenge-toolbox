import atexit
import logging
import os
import subprocess
import time
from collections import OrderedDict, defaultdict
from copy import deepcopy
from posixpath import join
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from toolbox.config.docker import FORWARD_PORTS
from toolbox.utils import parse_bool, fatal_error

from .utils import get_image_url, sorted_container_configs

BIND_ADDR = '127.0.0.1'
ULIMIT_NPROC = '2048:4096'
ULIMIT_NOFILE = '8192:16384'
SECRET = 'secret'

DEFAULT_MEMORY_LIMIT_MB = 100  # MiB
DEFAULT_CPUS_LIMIT = 1  # 100m requested, 1000m limit

CONNECTION_USAGE = defaultdict(lambda: 'nc ' + BIND_ADDR + ' %d')
CONNECTION_USAGE.update({
    'ssh': 'ssh -p %d user@' + BIND_ADDR + ' Password: ' + SECRET,
    'http': 'http://' + BIND_ADDR + ':%d',
})

# Hack to allow parallel executions. There are also such labels in production.
INSTANCE_LABEL = "com.avatao.instance_id"
INSTANCE_ID = uuid4()


def parse_crp_config(repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
    # This is not how things work anymore but the end result is the same...
    # The order is important because of namespace and volume sharing!
    crp_config = deepcopy(crp_config)
    contaner_configs = sorted_container_configs(crp_config)

    # Set all ports on the first container in the format below...
    # Also set absolute image URLs here
    ports = {}
    for short_name, crp_config_item in contaner_configs:
        crp_config_item['image'] = get_image_url(repo_name, repo_branch, short_name, crp_config_item)

        # Convert ['port/L7_proto'] format to {'port/L4_proto': 'L7_proto'}
        # * We do not differentiate udp at layer 7
        for port in crp_config_item.pop('ports', []):
            parts = port.lower().split('/', 1)
            proto_l7 = parts[1] if len(parts) == 2 else 'tcp'
            port_proto = join(parts[0], 'udp' if proto_l7 == 'udp' else 'tcp')
            ports[port_proto] = proto_l7

    # Set the ports in the first container's config.
    contaner_configs[0][1]['ports'] = ports
    return contaner_configs


def get_container_command(
    crp_config_item: Dict[str, Any], short_name: str, share_with: str = None
) -> Tuple[subprocess.Popen, str, str]:

    container_name = '-'.join((str(INSTANCE_ID), short_name))
    image = crp_config_item['image']

    command = [
        'docker', 'run',
        '-e', 'AVATAO_CHALLENGE_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'AVATAO_USER_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'AVATAO_INSTANCE_ID=%s' % INSTANCE_ID,
        '-e', 'AVATAO_SECRET=%s' % SECRET,
        '-e', 'SECRET=%s' % SECRET,  # for compatibility!
        '--name=%s' % container_name,
        '--label=%s=%s' % (INSTANCE_LABEL, INSTANCE_ID),
        '--cpus=%s' % round(int(crp_config_item.get('cpu_limit_ms', 1000)) / 1000, 2),
        '--memory=%s' % crp_config_item.get('mem_limit_mb', DEFAULT_MEMORY_LIMIT_MB) + 'M',
        '--cpus=%s' % DEFAULT_CPUS_LIMIT,
        '--ulimit=nproc=%s' % ULIMIT_NPROC,
        '--ulimit=nofile=%s' % ULIMIT_NOFILE,
    ]

    if 'ports' in crp_config_item and FORWARD_PORTS:
        for port, proto_l7 in crp_config_item['ports'].items():
            port_num = int(port.split('/')[0])
            command += ['-p', '%s:%d:%s' % (BIND_ADDR, port_num, port)]
            logging.info('Connection: %s', CONNECTION_USAGE[proto_l7] % port_num)

    if 'capabilities' in crp_config_item:
        command += ['--cap-drop=ALL']
        command += ['--cap-add=%s' % cap for cap in crp_config_item['capabilities']]

    if crp_config_item.get('read_only', False):
        command += ['--read-only']

    if share_with is None:
        # Disable DNS as there will be no internet access in production
        command += ['--dns=0.0.0.0', '--hostname=avatao']
    else:
        # Share the first container's network namespace and volumes
        command += [
            '--network=container:%s' % share_with,
            '--volumes-from=%s' % share_with,
        ]

    # Absolute URL of the image
    command += [image]
    return command, container_name


def poll_container(proc: subprocess.Popen, container_name: str, *, retries: int, sleeps: int):
    for i in range(0, retries):
        logging.debug('Waiting %ds for %s [%d/%d]', sleeps, container_name, i + 1, retries)
        time.sleep(sleeps)

        # Check whether the process exited
        if proc.poll() is not None:
            raise ValueError('Container exited!')

        try:
            # Check whether the container is running yet
            running: str = subprocess.check_output(
                ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
                stderr=subprocess.DEVNULL).decode('utf-8').strip()

            if parse_bool(running):
                break
        except subprocess.CalledProcessError:
            pass
    else:
        raise ValueError('Container timed out!')


def run_container(
    crp_config_item: Dict[str, Any], short_name: str, share_with: str = None
) -> Tuple[subprocess.Popen, str]:

    command, container_name = get_container_command(crp_config_item, short_name, share_with)
    image = crp_config_item['image']

    try:
        # Check whether the image exists to avoid horrific edge-cases
        image_output: str = subprocess.check_output(['docker', 'images', '-q', image]).decode('utf-8').rstrip()
        if not image_output:
            fatal_error('Image %s not found! Please, make sure it exists.' % image)

        logging.debug(' '.join(map(str, command)))
        proc = subprocess.Popen(command)

        # There is no God.
        poll_container(proc, container_name, retries=10, sleeps=5)
        # Ready but PID 1 might not be so wait some more...
        poll_container(proc, container_name, retries=1, sleeps=5)

        return proc, container_name

    except (subprocess.CalledProcessError, ValueError):
        fatal_error('Failed to run %s!' % image)


def remove_containers():
    subprocess.Popen(
        ['sh', '-c', 'docker rm -fv $(docker ps -aq --filter=label=%s=%s)' % (INSTANCE_LABEL, INSTANCE_ID)],
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()


def start_containers(repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]) -> Dict[str, subprocess.Popen]:
    proc_map, first = OrderedDict(), None
    for short_name, crp_config_item in parse_crp_config(repo_name, repo_branch, crp_config):
        proc, container_name = run_container(crp_config_item, short_name, share_with=first)
        proc_map[container_name] = proc
        if first is None:
            first = container_name

    return proc_map


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    os.chdir(repo_path)
    atexit.register(remove_containers)
    proc_map = start_containers(repo_name, repo_branch, config['crp_config'])

    logging.info('When you gracefully terminate this script [Ctrl+C] the containers will be destroyed.')
    for proc in proc_map.values():
        try:
            proc.wait()
        except KeyboardInterrupt:
            break
