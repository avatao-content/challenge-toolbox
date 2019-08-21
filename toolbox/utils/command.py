from importlib import import_module

from .config import read_config
from .utils import counted_error_at_exit, fatal_error, get_sys_args, init_logger


def _run_command(command: str, repo_path: str, repo_name: str, repo_branch: str, config: dict):
    crp_type = config.get("crp_type") or "static"
    try:
        module = import_module('.'.join(("toolbox", crp_type, command)))
    except ImportError:
        fatal_error("ImportError(crp_type=%s, command=%s)", crp_type, command)

    module.run(repo_path, repo_name, repo_branch, config)


def run(*commands):
    init_logger()
    repo_path, repo_name, repo_branch = get_sys_args()
    config = read_config(repo_path)

    for command in commands:
        _run_command(command, repo_path, repo_name, repo_branch, config)

    counted_error_at_exit()
