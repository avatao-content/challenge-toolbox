import os

CRP_DEPLOY_HOOK = os.getenv('CRP_DEPLOY_HOOK', 'https://next.avatao.com/api/v1/crpmanager/deploy')
CRP_DEPLOY_TOKEN = os.getenv('CRP_DEPLOY_TOKEN')

DOWNLOADABLE_FILES_BUCKET = os.getenv('DOWNLOADABLE_FILES_BUCKET', 'gs://avatao-challengestore-downloadable-files')

IS_CI = any(os.getenv(i, 'false').lower() in ('true', '1') for i in ('CI', 'CIRCLECI', 'DRONE'))

if 'DRONE_REPO_OWNER' in os.environ:
    REPO_OWNER = os.environ['DRONE_REPO_OWNER']
elif 'CIRCLE_PROJECT_USERNAME' in os.environ:
    REPO_OWNER = os.environ['CIRCLE_PROJECT_USERNAME']
else:
    REPO_OWNER = os.getenv('REPO_OWNER', 'avatao-content')

def ci_sys_args() -> (str, str, str):
    if 'DRONE_WORKSPACE' in os.environ:
        return os.environ['DRONE_WORKSPACE'], os.environ['DRONE_REPO_NAME'], os.environ['DRONE_BRANCH']
    if 'CIRCLE_WORKING_DIRECTORY' in os.environ:
        return os.environ['CIRCLE_WORKING_DIRECTORY'], os.environ['CIRCLE_PROJECT_REPONAME'], os.environ['CIRCLE_BRANCH']

    return os.getenv('WORKSPACE', os.getcwd()), os.environ['REPO_NAME'], os.environ['BRANCH_NAME']
