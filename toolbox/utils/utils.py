import glob
import logging
import os
import subprocess
import sys

import yaml

DEFAULT_TIMEOUT = 60 * 60  # timeout for commands

_error_counter = 0


def find_repo_path(base: str) -> str:
    """
    Find the first repo path (parent of config.yml) in a base directory

    :param base: base directory
    :return: the repo path
    """
    if os.path.exists(os.path.join(base, 'config.yml')):
        return base

    for item in glob.glob(os.path.join(base, '**', 'config.yml'), recursive=True):
        return os.path.dirname(item)

    logging.error('Could not find a repository in %s', base)
    sys.exit(1)


def get_repo_branch(repo_path: str) -> str:
    """
    Get the checked out branch of the repository

    :return string: branch
    """
    if os.getenv('DRONE', '0').lower() in ('true', '1'):
        return os.environ['DRONE_BRANCH']

    return subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'], cwd=repo_path)


def get_sys_args() -> (str, str):
    """
    Get parsed command line arguments

    Absolute repository path, repository name (optional)
    :return tuple: repo_path, repo_name
    """
    if os.getenv('DRONE', '0').lower() in ('true', '1'):
        return os.environ['DRONE_WORKSPACE'], os.environ['DRONE_REPO_NAME']

    if not 2 <= len(sys.argv) <= 3:
        logging.info('Usage: %s <git_repo_path> [docker_repo_name]', sys.argv[0])
        sys.exit(1)

    repo_path = find_repo_path(os.path.realpath(sys.argv[1]))
    repo_name = sys.argv[2] if len(sys.argv) >= 3 else os.path.basename(repo_path)

    return repo_path, repo_name


def run_cmd(args: list, timeout: int=DEFAULT_TIMEOUT, **kwargs) -> int:
    """
    Run the given command with subprocess.check_call

    :param args: list of args for Popen
    :param timeout: [optional] process timeout (defaults to DEFAULT_TIMEOUT)
    :param kwargs: [optional] additional key arguments
    :raise subprocess.CalledProcessError
    :return int
    """
    logging.debug('Running %s ...', ' '.join(map(str, args)))
    return subprocess.check_call(args, timeout=timeout, **kwargs)


def init_logger() -> None:
    """
    Configure the default python logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def counted_error(*args, **kwargs) -> None:
    """
    Wrapper for logging.error that will increase the error_counter
    """
    global _error_counter
    _error_counter += 1
    logging.error(*args, **kwargs)


def counted_error_at_exit() -> None:
    """
    Call at the end of execution to handle errors
    """
    logging.info('Finished with %d error(s).', _error_counter)
    sys.exit(1 if _error_counter > 0 else 0)


def fatal_error(*args, **kwargs) -> None:
    """
    Fatal error. Abort execution.
    """
    counted_error(*args, **kwargs)
    counted_error_at_exit()


def abort(*args, **kwargs) -> None:
    """
    Fatal error. Abort execution.
    """
    logging.info(*args, **kwargs)
    counted_error_at_exit()
