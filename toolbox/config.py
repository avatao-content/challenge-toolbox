import logging
import os
import re
import sys

import yaml

try:
    from packaging.version import parse as parse_version
except ImportError:
    from pkg_resources import parse_version

from toolbox.utils import counted_error


CONTROLLER_PROTOCOL = 'controller'

PROTOCOLS = {'udp', 'tcp', 'ssh', 'http', 'ws', CONTROLLER_PROTOCOL}


def read_config(path: str) -> dict:
    """
    Read the config.yml file

    :param path: path to the file or the base directory
    :return: dict
    """
    if os.path.isdir(path):
        path = os.path.join(path, 'config.yml')

    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)

        if parse_version(config["version"]) < parse_version('v3'):
            raise DeprecationWarning("config.yml v2 and below are deprecated, please upgrade to v3")

        return config

    except Exception as e:
        logging.exception(e)
        sys.exit(1)


def validate_ports(ports: list):
    for port in ports:
        try:
            port, protocol = port.split('/', 1)
            try:
                if not 0 < int(port) < 65536:
                    raise ValueError
            except Exception:
                counted_error('Invalid port number: %s. Ports must be numbers between 1 and 65535.', port)

            if protocol not in PROTOCOLS:
                counted_error('Invalid protocol in config.yml: %s. Valid protocols: %s', protocol, PROTOCOLS)

        except Exception:
            counted_error('Invalid port format. [port/protocol]')


def validate_bool(key, value):
    if str(value).lower() not in ('true', 'false', '1', '0'):
        counted_error('Invalid %s value. It must be boolean.', key)


def parse_bool(value) -> bool:
    return str(value).lower() in ('true', '1')


def validate_flag(config: dict, flag_required: bool = False):
    validate_bool('enable_flag_input', config.get('enable_flag_input'))

    if config.get('flag'):
        try:
            if config['flag'][0:6] == 'regex:':
                re.compile(config['flag'][6:])
        except TypeError:
            counted_error('Invalid flag value. It must be string.')
        except Exception:
            counted_error('Failed to compile regex flag.')

        if not parse_bool(config.get('enable_flag_input')):
            counted_error('enable_flag_input must be true for static flags.')

    elif flag_required:
        counted_error('A static (or regex) flag must be set.')
