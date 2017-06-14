#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; -*-

import atexit
import logging
import os
import posixpath
import subprocess
import sys
import time
import yaml


CONTROLLER_PORT = 5555

CONNECTION_USAGE = {
    'tcp': 'nc 127.0.0.1 %d',
    'http': 'http://127.0.0.1:%d',
    'ssh': 'ssh -p %d user@127.0.0.1 \n\n password: p\n'
}

_docker_repo_name = os.getenv('CI_BUILD_REPO', '/avatao/').split('/')[-2]
DOCKER_REPO = os.getenv('DOCKER_REPOSITORY', _docker_repo_name)


def _set_logger():

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def _read_config(key):

    config = None

    try:
        with open('./config.yml', 'r') as f:
            config = yaml.load(f)
    except FileNotFoundError as e:
        logging.error('Missing config.py')
        logging.error(e)

    return config[key] if config else None


def cleanup(repo_name):

    solvable = '%s-%s' % (repo_name, 'solvable')
    logging.info('Killing solvable...')
    subprocess.Popen(['docker', 'rm', '-fv', solvable]).wait()

    controller = '%s-%s' % (repo_name, 'controller')
    logging.info('Killing controller...')
    subprocess.Popen(['docker', 'rm', '-fv', controller]).wait()
    logging.info('Bye')


def _run_container(repo_name):

    solvable_name = '%s-%s' % (repo_name, 'solvable')

    solvable, controller = (None, None)
    for image_type in ('solvable', 'controller'):

        name = '%s-%s' % (repo_name, image_type)
        image = posixpath.join(DOCKER_REPO, name)

        dimg = ['docker', 'images', image]
        output = str(subprocess.check_output(dimg, universal_newlines=True, stderr=subprocess.STDOUT))

        if output.find(image) == -1:
            logging.warning('Could not find docker image %s. Skipping...' % image)
            continue

        logging.info('Starting %s...' % image_type)

        drun = ['docker',
                'run',
                '--rm',
                '--name', name,
                '-e', 'SECRET=secret',
                '--read-only',
                '--cap-drop', 'ALL']


        if image_type == 'solvable':
            # Network settings for the solvable
            drun += ['--dns', '0.0.0.0', '--hostname', 'avatao']

            # Add capabilities
            capabilities = _read_config('capabilities')
            capabilities = ['--cap-add=%s' % capability for capability in capabilities]
            drun += capabilities

            # Add solvable ports
            config_ports = _read_config('ports')
            ports = []
            for item in config_ports.items():
                ports += ['-p', '127.0.0.1:%s:%s' % (item[0], item[0])]
                conn_info = CONNECTION_USAGE[next(iter(item[1].keys()))] % item[0]
                logging.info('Solvable connection: %s' % conn_info)
            drun += ports

            # Expose the internal controller port via the solvable
            # because of the shared network namespace
            drun += ['-p', '127.0.0.1:%s:%s' % (CONTROLLER_PORT, CONTROLLER_PORT)]

        else:
            # Share the solvable's network namespace and volumes with the controller
            drun += ['--net', 'container:%s' % solvable_name,
                     '--volumes-from', solvable_name]
            logging.info('Controller connection: http://127.0.0.1:%d' % CONTROLLER_PORT)

        drun += [image]
        logging.debug('Command: %s' % ' '.join(drun))

        try:
            proc = subprocess.Popen(drun)

        except subprocess.CalledProcessError:
            logging.error('Failed to run %s. Please make sure that is was built.' % image_type)
            continue

        if image_type == 'solvable':
            solvable = proc
        else:
            controller = proc

        time.sleep(4)

    return solvable, controller


if __name__ == '__main__':
    """
    Run avatao solvable and controller docker images. Simply add the challenge repository path as the first
    argument and the script does the rest.

    Python dependencies:
        - PyYAML (http://pyyaml.org/) or simply `pip3 install PyYAML`
          (on Ubuntu you additionally need `apt-get install python3-yaml`)
    """

    _set_logger()

    if len(sys.argv) != 2:
        logging.info('Usage: ./start.py <repository_path>')
        sys.exit(1)

    os.chdir(sys.argv[1])
    repo_name = os.path.basename(os.path.realpath(sys.argv[1]))

    solvable, controller = _run_container(repo_name)
    atexit.register(cleanup, repo_name)

    logging.info('All up!')
    logging.info('When you gracefully (Ctrl+C) terminate this script, both containers will be destroyed.')
    logging.info('Container log: \n')

    if solvable:
      solvable.wait()
    if controller:
      controller.wait()
