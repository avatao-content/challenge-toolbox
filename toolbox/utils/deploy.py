import hashlib
import logging
import os
import functools
from glob import glob

import requests

from toolbox.config import CRP_DEPLOY_HOOK, CRP_DEPLOY_TOKEN, CRP_FILES_SALT, DOWNLOADABLE_FILES_BUCKET, ORGANIZATION

from .utils import fatal_error, run_cmd


@functools.lru_cache(maxsize=32)
def get_obfuscated_path_prefix(repo_name: str, repo_branch: str) -> str:
    if not CRP_FILES_SALT:
        fatal_error('CRP_FILES_SALT must be set!')

    secret = '/'.join((ORGANIZATION, repo_name, repo_branch, CRP_FILES_SALT)).encode('utf-8')
    return hashlib.sha512(secret).hexdigest()[:40]


def list_downloadable_files(repo_path: str, repo_name: str, repo_branch: str) -> list:
    return [
        '/'.join((get_obfuscated_path_prefix(repo_name, repo_branch), os.path.basename(path)))
        for path in glob(os.path.join(repo_path, 'downloads', '*'))
        if os.path.isfile(path)
    ]


def upload_files(repo_path: str, repo_name: str, repo_branch: str):
    downloads_path = os.path.join(repo_path, 'downloads')
    if glob(os.path.join(downloads_path, '*')):
        remote_path = '/'.join((DOWNLOADABLE_FILES_BUCKET, get_obfuscated_path_prefix(repo_name, repo_branch)))
        run_cmd(['gsutil', '-m', 'rsync', '-c', '-d', '-e', downloads_path + '/', remote_path + '/'])


def update_hook(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    if not CRP_DEPLOY_HOOK or not CRP_DEPLOY_TOKEN:
        fatal_error('CRP_DEPLOY_HOOK/CRP_DEPLOY_TOKEN must be set!')

    payload = {
        # Challenge Key
        'organization': ORGANIZATION,
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
