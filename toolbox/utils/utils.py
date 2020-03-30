import logging
import os
import subprocess
import sys
from glob import glob

from toolbox.config import ACTIVE_REMOTE_BRANCHES, DEFAULT_COMMAND_TIMEOUT, IS_CI, ci_sys_args

_error_counter = 0


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
    global _error_counter  # pylint: disable=global-statement
    _error_counter += 1
    logging.error(*args, **kwargs)


def get_error_counter() -> int:
    """
    Return the current number of non-fatal errors
    """
    return _error_counter


def counted_error_at_exit() -> None:
    """
    Call at the end of execution to handle errors
    """
    logging.info('Finished with %d error(s).', _error_counter)
    sys.exit(1 if _error_counter > 0 else 0)


def fatal_error(*args, **kwargs) -> None:
    """
    Abort execution with a fatal error
    """
    counted_error(*args, **kwargs)
    counted_error_at_exit()


def abort(*args, **kwargs) -> None:
    """
    Abort execution without an additional error
    """
    logging.info(*args, **kwargs)
    counted_error_at_exit()


def is_ci() -> bool:
    return os.getenv('DRONE', '0').lower() in ('true', '1')


def find_repo_path(base: str) -> str:
    """
    Find the first repo path (parent of config.yml) in a base directory

    :param base: base directory
    :return: the repo path
    """
    if os.path.exists(os.path.join(base, 'config.yml')):
        return base

    for item in glob(os.path.join(base, '**', 'config.yml'), recursive=True):
        return os.path.dirname(item)

    fatal_error('Could not find a repository in %s', base)


def get_repo_branch(repo_path: str) -> str:
    """
    Get the checked out branch of the repository

    :return string: branch
    """
    git_head_cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
    try:
        return subprocess.check_output(git_head_cmd, cwd=repo_path).decode('utf-8').rstrip()

    except subprocess.CalledProcessError:
        fatal_error('Failed to run: %s', git_head_cmd)


def get_sys_args() -> (str, str, str):
    """
    Get parsed command line arguments

    Absolute repository path, repository name (optional)
    :return tuple: repo_path, repo_name, repo_branch
    """
    if IS_CI:
        return ci_sys_args()

    if not 2 <= len(sys.argv) <= 4:
        logging.info('Usage: %s <repo_path> [repo_name] [repo_branch]', sys.argv[0])
        sys.exit(1)

    repo_path = find_repo_path(os.path.realpath(sys.argv[1]))
    repo_name = sys.argv[2] if len(sys.argv) >= 3 else os.path.basename(repo_path)
    repo_branch = sys.argv[3] if len(sys.argv) >= 4 else get_repo_branch(repo_path)

    return repo_path, repo_name, repo_branch


def abort_inactive_branch(repo_branch: str, *, allow_local: bool):
    # Allow local execution for some crp types - e.g.: docker
    if allow_local and not is_ci():
        return

    if repo_branch not in ACTIVE_REMOTE_BRANCHES:
        abort("Inactive branch: '%s' / %s", repo_branch, ACTIVE_REMOTE_BRANCHES)


def run_cmd(args: list, *, timeout: int = DEFAULT_COMMAND_TIMEOUT, raise_errors: bool = False, check_output: bool = False, **kwargs):
    """
    Run the given command with subprocess.check_call

    :param args: list of args for Popen
    :param timeout: [optional] process timeout (defaults to 1 hour)
    :param raise_errors: [optional] raise errors instead of exiting? (defaults to False)
    :param check_output: [optional] use check_output instead of check_call? (defaults to False)
    :param kwargs: [optional] additional key arguments
    :raise subprocess.CalledProcessError
    :return int
    """
    try:
        logging.debug('Running %s ...', args)
        if check_output:
            return subprocess.check_output(args, timeout=timeout, **kwargs)
        return subprocess.check_call(args, timeout=timeout, **kwargs)

    except subprocess.CalledProcessError:
        if raise_errors:
            raise
        fatal_error('Failed to run: %s', args)


def check_common_files(repo_path: str = None):
    if repo_path is None:
        repo_path = os.getcwd()

    if not glob(os.path.join(repo_path, '.drone.yml')):
        logging.warning('No .drone.yml file is found. This file is necessary for our automated tests,\n\t'
                        'please, get it from any template before uploading your challenge.')

    if not glob(os.path.join(repo_path, 'CHANGELOG')):
        logging.warning('No CHANGELOG file is found. If you modified an existing licensed challenge,\n\t'
                        'please, summarize what your changes were.')

    if not glob(os.path.join(repo_path, 'LICENSE')):
        logging.warning('No LICENSE file is found. Please add the (original) license file if you copied\n\t'
                        'a part of your challenge from a licensed challenge.')

    if not glob(os.path.join(repo_path, 'README.md')):
        logging.warning('No README.md file is found. Readmes help others to understand your challenge.')
