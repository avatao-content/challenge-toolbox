import os
import re
from toolbox.utils import parse_bool

from .deploy import IS_CI

# The main registry to push challenge images to.
DOCKER_REGISTRY = os.getenv('DOCKER_REGISTRY', 'eu.gcr.io/avatao-challengestore').rstrip('/')
# Optional set of registries to mirror DOCKER_REGISTRY for challenge clusters. Do not use these explicitly.
DOCKER_REGISTRY_MIRRORS = {i.rstrip('/') for i in re.split(r'[\s|,]', os.getenv('DOCKER_REGISTRY_MIRRORS', '')) if i}
# Allow other registries for external images in config.yml - such as the Tutorial Framework on Docker Hub.
# - Baseimages can be mirrored too where they are built.
WHITELISTED_DOCKER_REGISTRIES = [DOCKER_REGISTRY, "avatao", "docker.io/avatao"]

PULL_BASEIMAGES = parse_bool(os.getenv('TOOLBOX_PULL_BASEIMAGES', 'false'))
ENABLE_CPU_LIMITS = parse_bool(os.getenv('TOOLBOX_ENABLE_CPU_LIMITS', not IS_CI))
FORWARD_PORTS = parse_bool(os.getenv('TOOLBOX_FORWARD_PORTS', not IS_CI))
ARCHIVE_BRANCH = os.getenv('TOOLBOX_ARCHIVE_BRANCH', 'master')

CONFIG_KEYS = {'version', 'crp_type', 'crp_config', 'flag', 'enable_flag_input', 'downloads', 'archive'}
CRP_CONFIG_ITEM_KEYS = {'image', 'ports', 'buttons', 'mem_limit_mb', 'cpu_limit_ms', 'capabilities', 'read_only', 'volumes'}

CAPABILITIES = {
    # all linux capabilities:
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
