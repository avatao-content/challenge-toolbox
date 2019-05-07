import logging
import json
import os
import subprocess
from datetime import datetime
from glob import glob

from toolbox.utils import abort, fatal_error, get_repo_branch, run_cmd
from toolbox.utils.config import parse_bool
from toolbox.utils.deploy import update_hook
from toolbox.gce.config import *


# TODO: Allow JavaScript and Go.
def deploy_controller(repo_path: str, repo_name: str) -> list:
    controller_path = os.path.join(repo_path, 'controller')
    if len(glob(os.path.join(controller_path, '*'))):
        try:
            run_cmd(
                [
                    'gcloud', 'functions', 'deploy', repo_name,
                    f'--project={GOOGLE_PROJECT_ID}',
                    f'--region={CONTROLLER_FUNCTIONS_REGION}',
                    '--entry-point=main',
                    '--runtime=python37',
                    '--trigger-http'
                ],
                cwd=controller_path,
            )
        except subprocess.CalledProcessError:
            fatal_error('Failed to deploy %s/controller!', repo_name)


def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in ACTIVE_BRANCHES:
        abort("Inactive branch. Active branches: %s", ACTIVE_BRANCHES)

    deploy_controller(repo_path, repo_name)
    update_hook(repo_name, config)
