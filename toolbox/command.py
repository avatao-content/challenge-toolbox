import logging
import sys
from importlib import import_module

from toolbox.config import read_config
from toolbox.utils import counted_error_at_exit, get_sys_args, init_logger


def run():
    init_logger()
    command, repo_path, repo_name = get_sys_args()
    config = read_config(repo_path)
    crp_type = config.get("crp_type") or "static"
    try:
        module = import_module('.'.join(("toolbox", crp_type, command)))
    except ImportError:
        logging.error("Unknown crp_type(%s) or command(%s).", crp_type, command)
        sys.exit(1)

    module.run(repo_path, repo_name, config)
    counted_error_at_exit()
