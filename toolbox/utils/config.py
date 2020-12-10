import os
import re

import yaml

try:
    from packaging.version import parse as parse_version
except ImportError:
    from pkg_resources import parse_version

from toolbox.config.common import BUTTON_CONFIG_KEYS, CRP_TYPES, CURRENT_MAX_VERSION, CURRENT_MIN_VERSION, PROTOCOLS

from .utils import counted_error, fatal_error


def compare_version(config: dict, min_version: str, max_version: str):
    version = parse_version(config['version'])

    if version < parse_version(min_version):
        return -1
    if version > parse_version(max_version):
        return 1
    return 0


def validate_version(config: dict):
    cmp = compare_version(config, CURRENT_MIN_VERSION, CURRENT_MAX_VERSION)
    if cmp < 0:
        fatal_error('Please, upgrade to version %s with upgrade.py!', CURRENT_MIN_VERSION)
    if cmp > 0:
        fatal_error('Please, use a newer toolbox for version %s!', config['version'])


def get_crp_type(config: dict) -> str:
    crp_type = config.get('crp_type') or 'static'

    if crp_type not in CRP_TYPES:
        fatal_error("Unknown crp_type: '%s' / %s", crp_type, CRP_TYPES)

    return crp_type


def read_config(path: str, *, pre_validate: bool = True) -> dict:
    """
    Read the config.yml file

    :param path: path to the file or the base directory
    :param pre_validate: check version and crp_type fields
    :return: dict
    """
    if os.path.isdir(path):
        path = os.path.join(path, 'config.yml')

    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)

        if pre_validate:
            validate_version(config)
            get_crp_type(config)

        return config

    except Exception as e:
        fatal_error('%s(%s)', type(e).__name__, e)


def parse_bool(value) -> bool:
    return str(value).lower() in ('true', '1')


def validate_bool(key, value):
    if str(value).lower() not in ('true', 'false', '1', '0'):
        counted_error('Invalid %s value. It must be boolean.', key)


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


def validate_ports(ports: list, buttons: dict = None):  # pylint: disable=too-many-branches
    unique_ports = set()
    for port in ports:
        try:
            port, protocol = port.split('/', 1)
            unique_ports.add(port)
            try:
                if not 0 < int(port) < 65536:
                    raise ValueError
            except Exception:
                counted_error('Invalid port number: %s. Ports must be numbers between 1 and 65535.', port)

            if protocol not in PROTOCOLS:
                counted_error('Invalid protocol in config.yml: %s. Valid protocols: %s', protocol, PROTOCOLS)

        except Exception:
            counted_error('Invalid port format. [port/protocol]')

    if len(unique_ports) != len(ports):
        counted_error('Duplicate port numbers found.')

    if buttons is not None:
        if not isinstance(buttons, dict):
            counted_error('The buttons field must be a dict.')
        else:
            for button_key, button in buttons.items():
                if button_key not in ports:
                    counted_error('Button key %s is not found in ports.', button_key)

                for key in button.keys():
                    if key not in BUTTON_CONFIG_KEYS:
                        counted_error('Key %s is invalid for button %s.', key, button_key)
