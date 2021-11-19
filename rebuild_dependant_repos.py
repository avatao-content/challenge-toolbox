import os, sys, re
import requests
from github import Github

CIRCLECI_BASEURL = "https://circleci.com/api/v2"
CIRCLECI_ACCESS_TOKEN = os.environ["AVATAO_CIRCLECI_TOKEN"]
GITHUB_ACCESS_TOKEN = os.environ["AVATAO_GITHUB_TOKEN"]
g = Github(GITHUB_ACCESS_TOKEN)

if len(sys.argv) < 2:
    raise AttributeError("The image name is required as the first argument.")

image_name = sys.argv[1]
image_name = re.sub(r"[^a-zA-Z0-9-]", " ", image_name)

query = "org:avatao-content language:Dockerfile " + image_name

print("Searching GitHub with query: '%s'" % query)
code_search = g.search_code(query)

circleci_project_slugs = set()
for result in code_search:
    circleci_project_slugs.add(f"gh/{result.repository.organization.login}/{result.repository.name}")
print("Found %d candidate repositories." % len(circleci_project_slugs))

current_item = 1
for slug in circleci_project_slugs:
    print("[%d/%d] Triggering CI pipeline for: %s" % (current_item, len(circleci_project_slugs), slug))
    requests.post(f"{CIRCLECI_BASEURL}/project/{slug}/pipeline", headers={"Circle-Token": CIRCLECI_ACCESS_TOKEN})
    current_item += 1
