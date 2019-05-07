import os

ACTIVE_BRANCHES = ["master", "staging"]

DOCKER_REGISTRY = os.getenv('DOCKER_REGISTRY', 'eu.gcr.io/avatao-challengestore')

PULL_BASEIMAGES = os.getenv('TOOLBOX_PULL_BASEIMAGES', '0').lower() in ('true', '1')

CONFIG_KEYS = {'version', 'crp_type', 'crp_config', 'flag', 'enable_flag_input'}

CRP_CONFIG_ITEM_KEYS = {'image', 'ports', 'mem_limit_mb', 'capabilities', 'kernel_params', 'read_only'}

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

# Allowed kernel parameters to set via the --sysctl docker run option:
# This may be extended manually on a case-by-case basis.
KERNEL_PARAMETERS = {
    "net.ipv4.ip_forward",
}
