import logging
import os

import requests

from toolbox.utils.utils import fatal_error


def update_hook(repo_name: str, config: dict):
    try:
        crp_deploy_hook = os.environ['CRP_DEPLOY_HOOK']
        crp_deploy_token = os.environ['CRP_DEPLOY_TOKEN']
        payload = {
            # Challenge Key
            'organization': os.environ['DRONE_REPO_OWNER'],
            'repo_name': repo_name,
            'version': os.environ['DRONE_BRANCH'],
            # Challenge Config
            'config': config,
        }
    except KeyError as e:
        fatal_error('Missing environment variable: %s', e)

    logging.debug('Sending update hook to %s ...', crp_deploy_hook)
    logging.debug(payload)

    response = requests.post(
        url=crp_deploy_hook,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'X-Avatao-Token': crp_deploy_token,
        })

    if response.status_code not in (200, 204):
        fatal_error('%d %s: %s', response.status_code, response.reason, response.content)

    if response.status_code == 200:
        logging.debug(response.content)


def upload_files(repo_path: str):
    raise NotImplementedError
