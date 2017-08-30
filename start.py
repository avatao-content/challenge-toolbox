#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; -*-
from collections import defaultdict, OrderedDict
from posixpath import join
import atexit
import logging
import os
import subprocess
import sys
import time

from common import get_sys_args, get_image_url, read_config
from common import run_cmd, init_logger

BIND_ADDR = '127.0.0.1'
ULIMIT_NPROC = '2048:4096'
ULIMIT_NOFILE = '8192:16384'
MEMORY_LIMIT = '100M'
SECRET = 'secret'

CONNECTION_USAGE = defaultdict(lambda: 'nc ' + BIND_ADDR + ' %d')
CONNECTION_USAGE.update({
    'ssh': 'ssh -p %d user@' + BIND_ADDR + ' Password: ' + SECRET,
    'http': 'http://' + BIND_ADDR + ':%d',
})


def get_crp_config(repo_path: str, repo_name: str) -> dict:
    crp_config = read_config(repo_path)['crp_config']

    # The order is important because of namespace and volume sharing!
    crp_config_ordered = OrderedDict()

    # The main solvable always comes first if it's defined
    if 'solvable' in crp_config:
        crp_config_ordered['solvable'] = crp_config.pop('solvable')

    # Then the controller if it's defined
    if 'controller' in crp_config:
        crp_config_ordered['controller'] = crp_config.pop('controller')

    # Then any other solvable
    crp_config_ordered.update(crp_config)
    del crp_config

    # Set all ports on the first container in the format below...
    # Also set absolute image URLs here
    ports = {}
    for short_name, config in crp_config_ordered.items():

        if not isinstance(config, dict):
            raise TypeError('crp_config items must be dicts!')

        # Set the absolute image URL for this container
        if 'image' not in config:
            config['image'] = get_image_url(repo_name, short_name)
        else:
            config['image'] = get_image_url(config['image'])

        # Convert ['port/L7_proto'] format to {'port/L4_proto': 'L7_proto'}
        # * We do not differentiate udp at layer 7
        for port in config.pop('ports', []):
            parts = port.lower().split('/', 1)
            proto_l7 = parts[1] if len(parts) == 2 else 'tcp'
            port_proto = join(parts[0], 'udp' if proto_l7 == 'udp' else 'tcp')
            ports[port_proto] = proto_l7

    first = next(iter(crp_config_ordered.values()))
    first['ports'] = ports

    return crp_config_ordered


def run_container(short_name: str, crp_config_item: dict, share_with: str=None) \
        -> (subprocess.Popen, str):

    name = '-'.join((crp_config_item['image'].split('/')[-1].split(':')[0], short_name))
    drun = [
        'docker', 'run',
        '-e', 'CHALLENGE_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'USER_ID=00000000-0000-0000-0000-000000000000',
        '-e', 'SHORT_NAME=%s' % short_name,
        '-e', 'SECRET=%s' % SECRET,
        '--name=%s' % name,
        '--label=com.avatao.typed_crp_id=docker',
        '--memory=%s' % crp_config_item.get('mem_limit', MEMORY_LIMIT),
        '--ulimit=nproc=%s' % ULIMIT_NPROC,
        '--ulimit=nofile=%s' % ULIMIT_NOFILE,
        '--read-only',
    ]

    if 'ports' in crp_config_item:
        for port, proto_l7 in crp_config_item['ports'].items():
            port_num = int(port.split('/')[0])
            drun += ['-p', '%s:%d:%s' % (BIND_ADDR, port_num, port)]
            logging.info('Connection: %s' % CONNECTION_USAGE[proto_l7] % port_num)

    if 'capabilities' in crp_config_item:
        drun += ['--cap-drop=ALL']
        drun += ['--cap-add=%s' % cap for cap in crp_config_item['capabilities']]

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
    drun += [get_image_url(repo_name, short_name)]

    try:
        logging.debug(' '.join(map(str, drun)))
        proc = subprocess.Popen(drun)
        time.sleep(1)

        return proc, name

    except subprocess.CalledProcessError:
        logging.error('Failed to run %s. Please make sure that is was built.' % drun[-1])
        sys.exit(1)


def remove_containers():
    subprocess.Popen(
        ['sh', '-c', 'docker rm -fv $(docker ps -aq --filter=label=com.avatao.typed_crp_id=docker)'],
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()


if __name__ == '__main__':
    """
    Run avatao solvable and controller docker images. Simply add the challenge repository path as the first
    argument and the script does the rest.

    Python dependencies:
        - PyYAML (http://pyyaml.org/) or simply `pip3 install PyYAML`
          (on Ubuntu you additionally need `apt-get install python3-yaml`)
    """
    init_logger()
    repo_path, repo_name = get_sys_args()

    os.chdir(repo_path)
    atexit.register(remove_containers)

    proc_list = []
    first = None

    if 'crp_config' not in read_config(repo_path):
        logging.error("There is no crp_config in the config.yml,"
                      " if this is a static challenge you don't need to run it.")
        sys.exit(0)

    for short_name, crp_config_item in get_crp_config(repo_path, repo_name).items():
        proc, container = run_container(short_name, crp_config_item, share_with=first)
        proc_list.append(proc)
        if first is None:
            first = container

    logging.info('When you gracefully terminate this script [Ctrl+C] the containers will be destroyed.')

    for proc in proc_list:
        try:
            proc.wait()
        except KeyboardInterrupt:
            break
