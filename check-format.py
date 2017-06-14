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


CAPABILITIES = {'SETPCAP', 'SYS_MODULE', 'SYS_RAWIO', 'SYS_PACCT', 'SYS_ADMIN', 'SYS_NICE',
                'SYS_RESOURCE', 'SYS_TIME', 'SYS_TTY_CONFIG', 'MKNOD', 'AUDIT_WRITE',
                'AUDIT_CONTROL', 'MAC_OVERRIDE', 'MAC_ADMIN', 'NET_ADMIN', 'SYSLOG', 'CHOWN',
                'NET_RAW', 'DAC_OVERRIDE', 'FOWNER', 'DAC_READ_SEARCH', 'FSETID', 'KILL',
                'SETGID', 'SETUID', 'LINUX_IMMUTABLE', 'NET_BIND_SERVICE', 'NET_BROADCAST',
                'IPC_LOCK', 'IPC_OWNER', 'SYS_CHROOT', 'SYS_PTRACE', 'SYS_BOOT', 'LEASE',
                'SETFCAP', 'WAKE_ALARM', 'BLOCK_SUSPEND'} \
                - {'SYS_ADMIN', 'MAC_ADMIN', 'SYS_MODULE', 'SYS_RESOURCE'}

PORT_RANGE = {'min': 1, 'max': 65535}
PROTOCOLS = {'ssh', 'tcp', 'http'}
PROTOCOL_TYPES = {'embedded', 'raw'}

DIFFICULTY_RANGE = {'min': 10, 'max': 500}
FLAG_INPUTS = {'true', 'false'}

NAME_RANGE = {'min': 3, 'max': 200}
SUMMARY_RANGE = {'min': 30, 'max': 200}
DESCRIPTION_RANGE = {'min': 100, 'max': 30000}

VISIBILITIES = {'public', 'community_private', 'private'}

COST_SUM = 90
MIN_H2_NUM = 3

CONFIG_KEYS = {'version', 'capabilities', 'ports', 'difficulty', 'enable_flag_input', 'flag', 'name', 'visibility', 'community', 'skills', 'recommendations', 'owner', 'source_dependency'}

IP = '127.0.0.1'
CONTROLLER_PORT = 5555

DOCKER_REPO = os.getenv('DOCKER_REPOSITORY', '')


def _set_logger():

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def check_config(f, is_static):

    config = yaml.load(f)
    url_re = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)' \
                        r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]' \
                        r'+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

    invalid_keys = set(config.keys()) - set(CONFIG_KEYS)
    if len(invalid_keys) > 0:
        logging.error('Invalid key(s) found in config.yml: %s' % invalid_keys)

    # Version
    if config['version'] != 'v1':
        logging.error('Invalid version in config.yml. Valid value: v1')

    if not is_static:

        # Capabilities
        invalid_caps = set(config['capabilities']) - CAPABILITIES
        if len(invalid_caps) > 0:
            logging.error('Invalid capability in config.yml: %s. Valid values: %s', invalid_caps, CAPABILITIES)

        # Ports
        for item in config['ports'].items():
            try:
                assert int(item[0]) in range(PORT_RANGE['min'], PORT_RANGE['max'] + 1)
            except Exception:
                logging.error('Invalid ports in config.yml. '
                              'Valid values: %d - %d' % (PORT_RANGE['min'], PORT_RANGE['max']))

            if not isinstance(item[1], dict):
                logging.error('Invalid value type under ports in config.yml: Only dictionaries are allowed.')

            invalid_protocol = set(item[1].keys()) - PROTOCOLS
            if len(invalid_protocol) > 0:
                logging.error('Invalid protocol in config.yml: %s. Valid values: %s', invalid_protocol, PROTOCOLS)

            invalid_protocol_type = set(item[1].values()) - PROTOCOL_TYPES
            if len(invalid_protocol_type) > 0:
                logging.error('Invalid protocol type in config.yml: %s. '
                              'Valid values: %s', invalid_protocol_type, PROTOCOL_TYPES)

    # Difficulty
    try:
        assert int(config['difficulty']) in range(DIFFICULTY_RANGE['min'], DIFFICULTY_RANGE['max'] + 1)
    except Exception:
        logging.error('Invalid difficulty in config.yml. '
                      'Valid values: %d - %d' % (DIFFICULTY_RANGE['min'], DIFFICULTY_RANGE['max']))

    # Enable flag input
    if str(config['enable_flag_input']).lower() not in FLAG_INPUTS:
        logging.error('Invalid enable_flag_input in config.yml. Only boolean values are allowed.')

    # Flag
    if is_static:
        #  Check static flags for static challenges. Dynamic flags are checked in test controller test functions.
        try:
            assert isinstance(config['flag'], str)
        except AssertionError:
            logging.error('Invalid flag in config.yml. Flag should be a string')
        except KeyError:
            logging.error('Missing flag from config.yml. Static challenges should have a static flag set.')

    # Name
    try:
        assert len(config['name']) in range(NAME_RANGE['min'], NAME_RANGE['max'] + 1)
    except:
        logging.error('Invalid challenge name in config.yml. '
                      'Name should be a string with length %d - %d' % (NAME_RANGE['min'], NAME_RANGE['max']))


    if not isinstance(config['skills'], list):
        logging.error('Invalid skills in config.yml. Skills should be placed into a list.\n'
                      '\tValid skills are listed here: \n'
                      '\thttps://platform.avatao.com/api-explorer/#/api/core/skills/')

    if not isinstance(config['recommendations'], dict):
        logging.error('Invalid recommendations in config.yml. Recommendations should be added in the following '
                      'format:\n\n'
                      'recommendations:\n'
                      '\twww.example.com: \'Example webpage\'\n'
                      '\thttp://www.example2.com: \'Example2 webpage\''
                      '\thttp://example3.com: \'Example3 webpage\'')

    for item in config['recommendations'].items():
        if url_re.fullmatch(item[0]) is None:
            logging.error('Invalid recommended URL (%s) found in config.yml' % item[0])

        if not isinstance(item[1], str):
            logging.error('The name of recommended url (%s) should be a string in config.yml' % item[1])

    if not isinstance(config['owner'], list):
        logging.error('Challenge owners (%s) should be placed into a list in config.yml' % config['owner'])


def _check_writeup(f):

    w = f.read()

    # Check if writeup.md starts with the challenge name in H1 style.
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
        config_challenge_name = config['name']

        h1_pattern = '^%s\n={%d}\n\n' % (config_challenge_name, len(config_challenge_name))
        try:
            writeup_challenge_name = re.search('^.*\n', w).group()[:-1]
            assert writeup_challenge_name == config_challenge_name
            re.search(h1_pattern, w).group()
        except AssertionError:
            logging.error('The challenge names in writeup.md (%s) and config.yml (%s) have be the same.' %
                          (writeup_challenge_name, config_challenge_name))
        except Exception:
            logging.error('The challenge names in writeup.md have to be in H1 style. For example: \n\n'
                          'Challenge name\n'
                          '==============\n')

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

    if len(h2) < MIN_H2_NUM:
        logging.error('There should be at least %d sections in writeup.md' % MIN_H2_NUM)

    h2_last = h2.pop()
    if h2_last != '\n## Complete solution\n':
        logging.error('The last section should be called "Complete solution" in writeup.md')

    h2costs = [re.search(h2_pattern, h2cost).group()
               for h2cost in re.findall(h2_pattern + cost_pattern, w)]

    missing_costs = set(h2) - set(h2costs)
    if len(missing_costs) > 0:
        logging.error('No cost is defined in writeup.md for section(s): %s \n \tPlease make sure you have the following'
                      ' format (take care of the starting and ending newlines):\n %s' % (missing_costs, cost_pattern))


def _check_description(f):

    d = f.read()
    if len(d) not in range(DESCRIPTION_RANGE['min'], DESCRIPTION_RANGE['max'] + 1):
        logging.error('Description should be minimally %d, maximally %d characters long.',
                      DESCRIPTION_RANGE['min'], DESCRIPTION_RANGE['max'])

    # Description can contain maximally H4- or H5-style sections.
    maxh3_pattern = r'\n#{1,3} [A-Z].{5,150}\n'
    maxh3 = re.findall(maxh3_pattern, d)
    if maxh3:
        logging.error('Section name font size is too large in description.md. '
                      'Please use H4 (####) or H5 (#####) section names.'
                      '\n\tDetails: %s' % maxh3)

    # Check if newlines embrace section names
    minh4_nonewline_pattern = r'#{4,5} [A-Z].{5,150}'
    minh4_nonewline = set(re.findall(minh4_nonewline_pattern, d))

    minh4_pattern = r'\n\n#{4,5} [A-Z].{5,150}\n\n'
    minh4 = re.findall(minh4_pattern, d)

    invalid_sections = minh4_nonewline - set(''.join(minh4).split('\n'))
    if len(invalid_sections):
        logging.error('No starting or ending newline for section(s) in description.md: %s' % invalid_sections)


def check_metadata():

    # Check if metadata files exist
    try:
        with open('metadata/description.md', 'r', encoding='utf-8') as f:
            _check_description(f)

        with open('metadata/summary.md', 'r', encoding='utf-8') as f:
            s = f.read()
            if len(s) not in range(SUMMARY_RANGE['min'], SUMMARY_RANGE['max'] + 1):
                logging.error('Summary should be minimally %d, maximally %d characters long.',
                              SUMMARY_RANGE['min'], SUMMARY_RANGE['max'])

        with open('metadata/writeup.md', 'r', encoding='utf-8') as f:
            _check_writeup(f)

    except FileNotFoundError as e:
        logging.error('Missing %s from metadata.' % e.filename)
        sys.exit(1)

    except UnicodeDecodeError as e:
        logging.error('Could decode markdown text: \n\n%s \n\tDetails: %s' % (e.object, e))

    except Exception as e:
        logging.error('Could not read file in metadata. \n\tDetails: %s' % e)


def _check_dockerfile(filename):

    repo_pattern = 'FROM (docker\.io\/){,1}avatao'

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


def check_solvable():

    _check_dockerfile('solvable/Dockerfile')


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

    _check_dockerfile('controller/Dockerfile')

    static_flag = None

    # Check controller's server.py
    try:
        with open('config.yml') as f:
            config = yaml.load(f)
            static_flag = config['flag']

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
    is_static = (not (len(glob('solvable/Dockerfile')) or len(glob('controller/Dockerfile'))))
    if is_static and not len(glob('downloads/*')):
        logging.error('Static challenges should have a "downloads" directory to share challenge files with users')

    check_yml('config.yml', is_static)

    if not is_static:
        check_controller()
        check_solvable()

    check_metadata()
    check_misc()

if __name__ == '__main__':

    """
    Sanity check and test an avatao challenge repository. Simply add the challenge repository path as
    the first argument and the script does the rest.

    Python dependencies:
        - PyYAML (http://pyyaml.org/) or simply `pip3 install PyYAML`
          (on Ubuntu you additionally need `apt-get install python3-yaml`)
    """

    _set_logger()

    if len(sys.argv) != 2:
        logging.info('Usage: ./check.py <repository_path>')
        sys.exit(1)

    os.chdir(sys.argv[1])
    sanity_check()

    logging.info('Finished')
