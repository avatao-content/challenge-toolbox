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

from toolbox.utils import fatal_error

from .utils import get_image_url, sorted_container_configs

BIND_ADDR = '127.0.0.1'
ULIMIT_NPROC = '2048:4096'
ULIMIT_NOFILE = '8192:16384'
MEMORY_LIMIT = '100'
SECRET = 'secret'

CONNECTION_USAGE = defaultdict(lambda: 'nc ' + BIND_ADDR + ' %d')
CONNECTION_USAGE.update({
    'ssh': 'ssh -p %d user@' + BIND_ADDR + ' Password: ' + SECRET,
    'http': 'http://' + BIND_ADDR + ':%d',
})

# Hack to allow parallel executions. There are also such labels in production.
INSTANCE_LABEL = "com.avatao.instance_id"
INSTANCE_ID = uuid4()


def get_crp_config(repo_name: str, repo_branch: str, crp_config: Dict[str, Dict]) -> List[Tuple[Dict[str, Dict]]]:
    # This is not how things work anymore but the end result is the same...
    # The order is important because of namespace and volume sharing!
    crp_config = deepcopy(crp_config)
    contaner_configs = sorted_container_configs(crp_config)

    # Set all ports on the first container in the format below...
    # Also set absolute image URLs here
    ports = {}
    for short_name, crp_config_item in contaner_configs:
        # Set the absolute image URL for this container
        if 'image' not in crp_config_item:
            crp_config_item['image'] = get_image_url(repo_name, repo_branch, short_name)

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


def run_container(crp_config_item: Dict[str, Any], short_name: str, share_with: str = None) \
        -> Tuple[subprocess.Popen, str]:

    container_name = '-'.join((str(INSTANCE_ID), short_name))
    drun = [
        'docker', 'run',
        '-e', 'AVATAO_CHALLENGE_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'AVATAO_USER_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'AVATAO_INSTANCE_ID=%s' % INSTANCE_ID,
        '-e', 'AVATAO_SECRET=%s' % SECRET,
        '-e', 'SECRET=%s' % SECRET,  # for compatibility!
        '--name=%s' % container_name,
        '--label=%s=%s' % (INSTANCE_LABEL, INSTANCE_ID),
        '--memory=%s' % crp_config_item.get('mem_limit_mb', MEMORY_LIMIT) + 'M',
        '--ulimit=nproc=%s' % ULIMIT_NPROC,
        '--ulimit=nofile=%s' % ULIMIT_NOFILE,
    ]

    if 'ports' in crp_config_item:
        for port, proto_l7 in crp_config_item['ports'].items():
            port_num = int(port.split('/')[0])
            drun += ['-p', '%s:%d:%s' % (BIND_ADDR, port_num, port)]
            logging.info('Connection: %s', CONNECTION_USAGE[proto_l7] % port_num)

    if 'capabilities' in crp_config_item:
        drun += ['--cap-drop=ALL']
        drun += ['--cap-add=%s' % cap for cap in crp_config_item['capabilities']]

    if crp_config_item.get('read_only', False):
        drun += ['--read-only']

    if share_with is None:
        # Disable DNS as there will be no internet access in production
        drun += ['--dns=0.0.0.0', '--hostname=avatao']
    else:
        # Share the first container's network namespace and volumes
        drun += [
            '--network=container:%s' % share_with,
            '--volumes-from=%s' % share_with,
        ]

    # Absolute URL of the image
    drun += [crp_config_item['image']]

    try:
        logging.debug(' '.join(map(str, drun)))
        proc = subprocess.Popen(drun)
        time.sleep(5)
        return proc, container_name

    except subprocess.CalledProcessError:
        fatal_error('Failed to run %s. Please make sure that is was built.' % drun[-1])


def remove_containers():
    subprocess.Popen(
        ['sh', '-c', 'docker rm -fv $(docker ps -aq --filter=label=%s=%s)' % (INSTANCE_LABEL, INSTANCE_ID)],
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()


def start_containers(repo_name: str, repo_branch: str, config: dict) -> Dict[str, subprocess.Popen]:
    proc_map, first = OrderedDict(), None
    for short_name, crp_config_item in get_crp_config(repo_name, repo_branch, config['crp_config']):
        proc, container_name = run_container(crp_config_item, short_name, share_with=first)
        proc_map[container_name] = proc
        if first is None:
            first = container_name

    return proc_map


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    os.chdir(repo_path)
    atexit.register(remove_containers)
    proc_map = start_containers(repo_name, repo_branch, config)

    logging.info('When you gracefully terminate this script [Ctrl+C] the containers will be destroyed.')
    for proc in proc_map.values():
        try:
            proc.wait()
        except KeyboardInterrupt:
            break
