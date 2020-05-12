import functools
import hashlib
import logging
import os
import subprocess

import requests

from toolbox.config import CRP_DEPLOY_HOOK, CRP_DEPLOY_TOKEN, DOWNLOADABLE_FILES_BUCKET, REPO_OWNER

from .utils import fatal_error, run_cmd


def _hash_directory(path):
    digest = hashlib.sha1()
    for root, _, files in os.walk(path):
        for names in files:
            file_path = os.path.join(root, names)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    while True:
                        buf = f.read(1024 * 1024)
                        if not buf:
                            break
                        digest.update(buf)

    return digest.hexdigest()


@functools.lru_cache(maxsize=8)
def _get_downloads_path_prefix(repo_path: str, repo_name: str, repo_branch: str) -> str:
    challenge_key_hash = hashlib.sha1('/'.join((REPO_OWNER, repo_name, repo_branch)).encode('utf-8')).hexdigest()
    downloads_hash = _hash_directory(os.path.join(repo_path, 'downloads'))
    return '/'.join((challenge_key_hash, downloads_hash))


def list_downloadable_files(repo_path: str, repo_name: str, repo_branch: str) -> list:
    downloads_path = os.path.join(repo_path, 'downloads')
    result = []
    for root, _, files in os.walk(downloads_path):
        prefix = _get_downloads_path_prefix(repo_path, repo_name, repo_branch)
        for filename in files:
            relpath = os.path.relpath(os.path.join(root, filename), downloads_path)
            result.append('/'.join((prefix, relpath)))
    return result


def upload_files(repo_path: str, repo_name: str, repo_branch: str):
    downloads_path = os.path.join(repo_path, 'downloads')
    if not list(os.walk(downloads_path)):
        return

    challenge_key_prefix, downloads_hash = _get_downloads_path_prefix(repo_path, repo_name, repo_branch).split('/')
    gs_parent_path = '/'.join((DOWNLOADABLE_FILES_BUCKET, challenge_key_prefix))
    gs_target_path = '/'.join((gs_parent_path, downloads_hash))

    try:
        ls_current = run_cmd(['gsutil', 'ls', gs_parent_path], raise_errors=True, check_output=True)
        current_content = list(map(lambda s: s.rstrip('/'), ls_current.decode('utf-8').rstrip().split('\n')))
    except subprocess.CalledProcessError:
        current_content = []

    if gs_target_path not in current_content:
        run_cmd(['gsutil', 'cp', '-r', downloads_path, gs_target_path])
        if current_content:
            run_cmd(['gsutil', 'rm', '-r', *current_content])


def update_hook(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    if not CRP_DEPLOY_HOOK or not CRP_DEPLOY_TOKEN:
        fatal_error('CRP_DEPLOY_HOOK/CRP_DEPLOY_TOKEN must be set!')

    payload = {
        # Challenge Key
        'repo_owner': REPO_OWNER,
        'repo_name': repo_name,
        'version': repo_branch,
        # Challenge Config
        'config': config,
        'files': list_downloadable_files(repo_path, repo_name, repo_branch),
    }

    logging.debug('Sending update hook to %s ...', CRP_DEPLOY_HOOK)
    logging.debug(payload)

    response = requests.post(
        url=CRP_DEPLOY_HOOK,
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'X-Avatao-Token': CRP_DEPLOY_TOKEN,
        })

    if response.status_code not in (200, 204):
        fatal_error('%d %s: %s', response.status_code, response.reason, response.content)

    if response.status_code == 200:
        logging.debug(response.content)
