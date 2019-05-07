import collections
import hashlib
import json
import logging
import os
import subprocess
import sys

import requests

from .utils import fatal_error


CRP_DEPLOY_HOOK = os.environ['CRP_DEPLOY_HOOK']

CRP_DEPLOY_TOKEN = os.environ['CRP_DEPLOY_TOKEN']


# TODO: Upload static challenge files here!


def walk_dir_and_hash_files(root_path: str) -> {str: {str: str}}:
    algo_list = ['md5', 'sha1', 'sha256']
    files = {}

    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            h = {algo: getattr(hashlib, algo)() for algo in algo_list}
            abspath = os.path.join(dirpath, filename)
            relpath = os.path.relpath(abspath, root_path)

            with open(abspath, 'rb') as file_:
                while True:
                    buffer = file_.read(4096)
                    if not buffer:
                        break
                    for algo in algo_list:
                        h[algo].update(buffer)

            files[relpath] = {algo: h[algo].hexdigest() for algo in algo_list}

    return files


def update_hook(repo_name: str, config: dict):
    # List of downloadable files
    downloads = walk_dir_and_hash_files('downloads')
    # Build a request for the web hook...
    data = {
        'repo_name': repo_name,
        'repo_owner': os.environ['DRONE_REPO_OWNER'],
        'repo_commit': os.environ['DRONE_COMMIT'],
        'config': config,
        'downloads': downloads,
    }
    template = json.dumps({'template': {'data': [
        {'name': key, 'value': value} for key, value in data.items()
    ]}})

    logging.info('Sending update hook to %s ...' % CRP_DEPLOY_HOOK)
    logging.debug(template)

    response = requests.post(
        url=CRP_DEPLOY_HOOK,
        data=template.encode('utf-8'),
        method='POST',
        headers={
            'Content-Type': 'application/vnd.collection+json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'X-Avatao-Token': CRP_DEPLOY_TOKEN,
        })

    if response.status_code != 200:
        fatal_error('%d %s: %s', response.status_code, response.reason, response.content)
