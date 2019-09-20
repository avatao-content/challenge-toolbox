import os

DOWNLOADABLE_FILES_BUCKET = os.getenv('DOWNLOADABLE_FILES_BUCKET', 'gs://avatao-challengestore-downloadable-files')
ORGANIZATION = os.getenv('DRONE_REPO_OWNER', 'avatao-content')

IS_CI = os.getenv('DRONE', 'false').lower() in ('true', '1')

CRP_DEPLOY_HOOK = os.getenv('CRP_DEPLOY_HOOK')
CRP_DEPLOY_TOKEN = os.getenv('CRP_DEPLOY_TOKEN')

def ci_sys_args() -> (str, str, str):
    return os.environ['DRONE_WORKSPACE'], os.environ['DRONE_REPO_NAME'], os.environ['DRONE_BRANCH']
