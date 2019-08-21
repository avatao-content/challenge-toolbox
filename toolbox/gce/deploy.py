import os
from glob import glob

from toolbox.gce.config import CONTROLLER_FUNCTIONS_REGION, GOOGLE_PROJECT_ID
from toolbox.utils import abort_inactive_branch, run_cmd
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
    abort_inactive_branch(repo_branch, allow_local=False)

    config['image'] = '-'.join((repo_name, repo_branch))
    deploy_controller(repo_path, config['image'])

    upload_files(repo_path, repo_name, repo_branch)
    update_hook(repo_name, repo_branch, config)
