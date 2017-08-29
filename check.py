#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; -*-
import json
import logging
import os
import re
import subprocess
import sys
from glob import glob as glob

import yaml

from common import get_sys_args, read_config
from common import run_cmd, init_logger


CAPABILITIES = {  # all linux capabilities:
    'SETPCAP', 'SYS_MODULE', 'SYS_RAWIO', 'SYS_PACCT', 'SYS_ADMIN', 'SYS_NICE',
    'SYS_RESOURCE', 'SYS_TIME', 'SYS_TTY_CONFIG', 'MKNOD', 'AUDIT_WRITE',
    'AUDIT_CONTROL', 'MAC_OVERRIDE', 'MAC_ADMIN', 'NET_ADMIN', 'SYSLOG', 'CHOWN',
    'NET_RAW', 'DAC_OVERRIDE', 'FOWNER', 'DAC_READ_SEARCH', 'FSETID', 'KILL',
    'SETGID', 'SETUID', 'LINUX_IMMUTABLE', 'NET_BIND_SERVICE', 'NET_BROADCAST',
    'IPC_LOCK', 'IPC_OWNER', 'SYS_CHROOT', 'SYS_PTRACE', 'SYS_BOOT', 'LEASE',
    'SETFCAP', 'WAKE_ALARM', 'BLOCK_SUSPEND',
} - {  # blacklisted capabilities (subject to change):
    'MAC_ADMIN', 'MAC_OVERRIDE', 'SYS_ADMIN', 'SYS_MODULE', 'SYS_RESOURCE',
    'LINUX_IMMUTABLE', 'SYS_BOOT', 'BLOCK_SUSPEND', 'WAKE_ALARM',
}

PORT_RANGE = {'min': 1, 'max': 65535}
CONTROLLER_PROTOCOL = 'controller'

COST_SUM = 90
MIN_WRITEUP_SECTIONS = 3


def check_config(path, is_static):
    config = read_config(path)

    if config['version'][:1] != 'v':
        logging.error('Invalid version. The version number must start with the letter v')
    elif config['version'] == 'v1':
        logging.error('This version is deprecated, please use v2.0.0')
    elif config['version'] != 'v2.0.0':
        logging.error('Invalid version. The supplied config version is not supported')

    if not is_static:
        controller_found = False
        for item in config['crp_config'].values():

            if not isinstance(item, dict):
                logging.error('Items of crp_config must be dicts.')

            if 'image' in item and item['image'].find('/') < 0:
                logging.error('If the image is explicitly defined, it must be relative '
                              'to the registry - e.g. challenge:solvable.')

            if 'capabilities' in item:
                invalid_caps = set(item['capabilities']) - CAPABILITIES
                if len(invalid_caps) > 0:
                    logging.error('Invalid capabilities: %s. Valid values: %s', invalid_caps, CAPABILITIES)

            for port in item.get('ports', []):
                try:
                    port, proto = port.split('/', 1)
                    try:
                        port = int(port)
                    except Exception:
                        logging.error('Invalid port. The port should be a number between 1 and 65535')

                    if PORT_RANGE['min'] > port or PORT_RANGE['max'] < port:
                        logging.error('Invalid port. The port should be a number between 1 and 65535')

                    if proto == CONTROLLER_PROTOCOL:
                        controller_found = True
                except Exception:
                    logging.error('Invalid port format. [port/protocol]')

        if not config.get('flag') and not controller_found:
            logging.error('Missing controller port [5555/%s] for a dynamic challenge.' % CONTROLLER_PROTOCOL)

    if str(config.get('enable_flag_input')).lower() not in ('true', 'false', '1', '0'):
        logging.error('Invalid enable_flag_input. Should be a boolean.')

    if is_static:
        try:
            assert isinstance(config['flag'], str)
        except AssertionError:
            logging.error('Invalid flag. Should be a string.')
        except KeyError:
            logging.error('Missing flag. Static challenges must have a static flag set.')


def check_writeup(f):
    w = f.read()

    # Check if costs and H2 sections are correct in writeup.md
    cost_pattern = '\nCost: [0-9]{1,2}%\n'
    costs = [int(re.search(r'[0-9]{1,2}', cost).group())
             for cost in re.findall(cost_pattern, w)]
    if sum(costs) != COST_SUM:
        logging.error('The sum of costs in writeup.md should be %d%%. \n \tPlease make sure you have the following'
                      ' format (take care of the white spaces, starting and ending newlines):\n %s' % (COST_SUM,
                                                                                                       cost_pattern))

    h2_pattern = r'\n## [A-Z].{5,150}\n'
    h2 = re.findall(h2_pattern, w)

    if len(h2) < MIN_WRITEUP_SECTIONS:
        logging.error('There should be at least %d sections in writeup.md' % MIN_WRITEUP_SECTIONS)

    h2_last = h2.pop()
    if h2_last != '\n## Complete solution\n':
        logging.error('The last section should be called "Complete solution" in writeup.md')

    h2costs = [re.search(h2_pattern, h2cost).group()
               for h2cost in re.findall(h2_pattern + cost_pattern, w)]

    missing_costs = set(h2) - set(h2costs)
    if len(missing_costs) > 0:
        logging.error('No cost is defined in writeup.md for section(s): %s \n \tPlease make sure you have the following'
                      ' format (take care of the starting and ending newlines):\n %s' % (missing_costs, cost_pattern))


def check_dockerfile(filename):
    repo_pattern = 'FROM (docker\.io\/)?avatao\/'

    try:
        with open(filename, 'r') as f:
            d = f.read()
            if re.search(repo_pattern, d) is None:
                logging.error('Please use avatao base images for your challenges. Our base images'
                              ' are available at https://hub.docker.com/u/avatao/')
    except FileNotFoundError as e:
        logging.error('Could not open %s' % e.filename)

    except Exception as e:
        logging.error('An error occurred while loading %s. \n\tDetails: %s' % (filename, e))


def _http_request(url):
    # Check controller's test endpoint.
    curl = ['curl', '-s']

    if url[-4:] == 'test':
        method = 'GET'
        func = 'Test'
    else:
        method = 'POST'
        func = 'Solution checker'
        curl += ['-X POST']

    curl += [url]

    try:
        output = subprocess.check_output(curl).decode('utf-8')
        logging.info('%s output: \n\n%s' % (func, output))

        # Check if solution checker returns a well-formatted JSON response
        solved = False
        if func == 'Solution checker':
            response = json.loads(output)
            solved = bool(response['solved'])
            assert isinstance(response['message'], str)

    except subprocess.CalledProcessError as e:
        logging.error('Curl returned with error. \n\tDetails: %s' % e)

    except OSError as e:
        logging.error('Curl returned with error. \n\tDetails: %s' % e)

    except ValueError as e:
        logging.error('Could not parse the response of solution checker. Bad JSON format. \n\tDetails: %s' % e)

    except NameError as e:
        logging.error('JSON attribute "solved" must be a boolean value. \n\tDetails: %s' % e)

    except KeyError as e:
        if e.args[0] == 'solved':
            logging.error('JSON key "%s" is missing from solution checker response. ' % e.args[0])
        elif e.args[0] == 'message':
            logging.warning('JSON key "%s" is missing from solution checker response. \n\t  In certain cases '
                            '(e.g., programming challenges) messages help users to complete the challenge.' % e.args[0])
    except AssertionError:
        logging.error('JSON attribute "message" must be a string value.')

    else:

        if (re.search('OK', output) and func == 'Test') or solved:
            logging.info('%s endpoint passed!' % func)
        elif re.search('404', output) and func == 'Test':
            logging.warning('Test endpoint is not found. '
                            '\n\t  Please implement it so as to make sure your challenge is working correctly.')
        elif re.search('405', output):
            logging.error('%s endpoint should implement HTTP %s.' % (func, method))
        elif re.search('500', output) or not solved:
            logging.error('%s endpoint failed!' % func)


def check_controller():
    # TODO: this is an unfinished migrated function!
    check_dockerfile('controller/Dockerfile')
    static_flag = None

    try:
        static_flag = read_config()['flag']

    except KeyError:
        logging.warning('Missing flag from config.yml. \n\t  You should implement a dynamic '
                        'solution checker (e.g., with random flags, unit tests) in the controller.')

    except FileNotFoundError as e:
        logging.error('Could not open %s' % e.filename)

    try:
        with open('controller/opt/server.py') as f:
            s = f.read()

    except FileNotFoundError as e:
        logging.error('Could not open %s' % e.filename)

    except Exception as e:
        logging.error('An error occurred while checking controller/opt/server.py. \n\tDetails: %s' % e)

    else:
        # Invoke test endpoint
        _http_request('http://%s:%d/secret/test' % (IP, CONTROLLER_PORT))

        # Check controller's solution_check endpoint.
        solution_check_pattern = 'def solution_check\(\):'
        solution_check = re.findall(solution_check_pattern, s)

        if not (solution_check or static_flag):
            logging.error('Function "solution_check()" is missing from controller/opt/server.py. '
                          '\n\tPlease implement it and check user solutions dynamically (e.g., random flag '
                          'checking)\n\tor insert a static flag into config.yml.')
        elif solution_check and not static_flag:
            # Invoke the solution checker when no static flag is used (e.g., programming challenges)
            _http_request('http://%s:%d/secret' % (IP, CONTROLLER_PORT))


def check_misc():
    if not len(glob('src/*')):
        logging.warning('Missing or empty "src" directory. Please place your source files there '
                        'if your challenge has any. ')

    if not len(glob('README.md')):
        logging.warning('No README.md file is found. Readmes help others to understand your challenge.')

    if not len(glob('LICENSE')):
        logging.warning('No LICENSE file is found. Please add the (original) license file if you copied'
                        '\n\t  a part of your challenge from a licensed challenge.')

    if not len(glob('CHANGELOG')):
        logging.warning('No CHANGELOG file is found. If you modified an existing licensed challenge, please summarize '
                        '\n\t  what your changes were.')


def check_yml(filename, is_static: bool=False):
    try:
        with open(filename, 'r') as f:
            check_config(f, is_static)

    except FileNotFoundError as e:
        logging.error('Could not open %s' % e.filename)

    except KeyError as e:
        logging.error('Key "%s" is missing from %s' % (e.args[0], filename))

    except Exception as e:
        logging.error('An error occurred while loading %s. \n\tDetails: %s' % (filename, e))


def sanity_check():

    # Check if the challenge is static
    is_static = (len(glob('solvable*/Dockerfile')) + glob('controller*/Dockerfile') > 0)
    if is_static and not len(glob('downloads/*')):
        logging.error('Static challenges should have a "downloads" directory for sharing challenge files with users.')

    check_yml('config.yml', is_static)
    check_config('config.yml', is_static)
    check_misc()

if __name__ == '__main__':
    """
    Sanity check and test an avatao challenge repository. Simply add the challenge repository path as
    the first argument and the script does the rest.

    Python dependencies:
        - PyYAML (http://pyyaml.org/) or simply `pip3 install PyYAML`
          (on Ubuntu you additionally need `apt-get install python3-yaml`)
    """
    init_logger()

    repo_path, repo_name = get_sys_args()
    os.chdir(repo_path)
    sanity_check()

    logging.info('Finished')
