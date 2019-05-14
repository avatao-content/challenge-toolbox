import os
from glob import glob

from toolbox.gce.config import DEPLOY_BRANCHES, CONTROLLER_FUNCTIONS_REGION, GOOGLE_PROJECT_ID
from toolbox.utils import abort, get_repo_branch, run_cmd
from toolbox.utils.deploy import update_hook, upload_files


# TODO: Allow JavaScript and Go.
def deploy_controller(repo_path: str, repo_name: str) -> list:
    controller_path = os.path.join(repo_path, 'controller')
    if glob(os.path.join(controller_path, '*')):
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


def run(repo_path: str, repo_name: str, config: dict):
    if get_repo_branch(repo_path) not in DEPLOY_BRANCHES:
        abort("Inactive branch. Active branches: %s", DEPLOY_BRANCHES)

    deploy_controller(repo_path, repo_name)
    update_hook(repo_name, config)
    upload_files(repo_path)
