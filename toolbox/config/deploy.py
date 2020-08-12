import os

CRP_DEPLOY_HOOK = os.getenv('CRP_DEPLOY_HOOK', 'https://next.avatao.com/api/v1/crpmanager/deploy')
CRP_DEPLOY_TOKEN = os.getenv('CRP_DEPLOY_TOKEN')

DOWNLOADABLE_FILES_BUCKET = os.getenv('DOWNLOADABLE_FILES_BUCKET', 'gs://avatao-challengestore-downloadable-files')

IS_CI = any(os.getenv(i, 'false').lower() in ('true', '1') for i in ('CI', 'CIRCLECI', 'DRONE'))

if 'REPO_OWNER' in os.environ:
    REPO_OWNER = os.environ['REPO_OWNER']
elif 'CIRCLE_PROJECT_USERNAME' in os.environ:
    REPO_OWNER = os.environ['CIRCLE_PROJECT_USERNAME']
elif 'DRONE_REPO_OWNER' in os.environ:
    REPO_OWNER = os.environ['DRONE_REPO_OWNER']
else:
    REPO_OWNER = 'avatao-content'
