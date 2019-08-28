from importlib import import_module

from .config import get_crp_type, read_config
from .utils import counted_error_at_exit, get_error_counter, get_sys_args, init_logger


def _run_command(command: str, repo_path: str, repo_name: str, repo_branch: str, config: dict):
    module_path = '.'.join(('toolbox', get_crp_type(config), command))
    module = import_module(module_path)
    module.run(repo_path, repo_name, repo_branch, config)

    if get_error_counter() > 0:
        counted_error_at_exit()


def run(*commands):
    init_logger()
    repo_path, repo_name, repo_branch = get_sys_args()
    config = read_config(repo_path)

    for command in commands:
        _run_command(command, repo_path, repo_name, repo_branch, config)

    counted_error_at_exit()
