import os
from glob import glob

from toolbox.gce.config import DEPLOY_BRANCHES, CONTROLLER_FUNCTIONS_REGION, GOOGLE_PROJECT_ID
from toolbox.utils import abort, run_cmd
from toolbox.utils.deploy import update_hook, upload_files


# TODO: Allow JavaScript and Go.
def deploy_controller(repo_path: str, image: str) -> list:
    controller_path = os.path.join(repo_path, 'controller')
    if glob(os.path.join(controller_path, '*.py')):
        run_cmd(
            [
                'gcloud', 'functions', 'deploy', image,
                f'--project={GOOGLE_PROJECT_ID}',
                f'--region={CONTROLLER_FUNCTIONS_REGION}',
                '--entry-point=main',
                '--runtime=python37',
                '--trigger-http'
            ],
            cwd=controller_path,
        )


def run(repo_path: str, repo_name: str, repo_branch: str, config: dict):
    if repo_branch not in DEPLOY_BRANCHES:
        abort("Inactive branch: '%s' / %s", repo_branch, DEPLOY_BRANCHES)

    config['image'] = '-'.join((repo_name, repo_branch))
    deploy_controller(repo_path, config['image'])

    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_name, repo_branch, config)
