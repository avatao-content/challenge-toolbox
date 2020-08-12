# Build Pipeline Environment

The challenge-toolbox is a python library to build and deploy challenges. It can be customized via environment variables. Basically, all that is required is to run deploy.py in your CI.

The best option is to use a container based CI system in which you can use a docker image as the build environment. In this case you only have to "docker build" the challenge-toolbox and use the resulting image as the build environment. Of course, you still need to set some environment variables. Another option is to skip docker and directly run deploy.py in whatever CI system you use. Out of the box, CircleCI, Drone and Google Cloud Build are supported but any other CI system can be used with the environment variables below.

## Requirements

* Docker is configured in the build environment:
  - Docker CLI / client is installed.
  - DOCKER_HOST and TLS environment variables are set if necessary.
* The build environment has push access to the container registry, including mirrors.
* The Challenge Infrastructure has pull access to the same container registry or its mirrors.
* The build environment has sufficient resources to build and run a few docker images.

## Environment variables

* `CRP_DEPLOY_TOKEN="CUSTOMER_SECRET_TOKEN"`
* `DOCKER_REGISTRY="docker.registry"`
* `REPO_OWNER="ChallengeKey.repo_owner"` # Optional in supported CI.
* `CI="true"` # Optional in supported CI.

### Optional environment variables

* `CRP_DEPLOY_HOOK="https://next.avatao.com/api/v1/crpmanager/deploy"`
* `DOCKER_REGISTRY_MIRRORS="optional.mirror.docker.registry"`
* `TOOLBOX_ARCHIVE_BRANCH="master"` # Legacy version to import instead of building.
* `TOOLBOX_FORWARD_PORTS="false"` # Disable port-forwarding in start.py for this context.
* `TOOLBOX_PULL_BASEIMAGES="true"` # Always pull base images before building.
* `WORKSPACE="$PWD"` # Path to the challenge git repository - defaults to the current directory.
  
### Environment variables for entrypoint.sh

* `DOCKER_LOGIN_[ID]_SERVER=eu.gcr.io` # A docker registry to log into.
* `DOCKER_LOGIN_[ID]_USERNAME=_json_key` # A corresponding registry username.
* `DOCKER_LOGIN_[ID]_PASSWORD=service_account_secret` # A corresponding registry password.
* `GOOGLE_APPLICATION_CREDENTIALS=/path/to/google_service_account_key.json`
* `GOOGLE_SERVICE_ACCOUNT_KEY=JSON_SECRET`  # Instead of GOOGLE_APPLICATION_CREDENTIALS.
* `GOOGLE_PROJECT_ID=google-project` # Google project ID to use.

## Downloadable files for challenges

The challenge-toolbox currently only has the ability to upload downloadable files to Avatao’s cloud storage. This is not possible from within the customers infrastructure. However, the challenge config file (config.yml) can be used to manually set downloadable file URLs with the "downloads" key containing a list of absolute URLs (https://...).
