import os.path
import json
import subprocess
import requests
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITHUB_HANDLE = os.environ.get("GITHUB_HANDLE")
GITHUB_KEY_TITLE = os.environ.get("GITHUB_KEY_TITLE")
GITHUB_KEY_PATH = os.environ.get("GITHUB_KEY_PATH")
GITHUB_API_URL = os.environ.get("GITHUB_API_URL")

GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
GITLAB_HANDLE = os.environ.get("GITLAB_HANDLE")
GITLAB_REMOTE = os.environ.get("GITLAB_REMOTE")
GITLAB_URL = os.environ.get("GITLAB_URL")
GITLAB_URL_PROTOCOL = os.environ.get("GITLAB_URL_PROTOCOL")
GITLAB_SSH_PORT = os.environ.get("GITLAB_SSH_PORT")
GITLAB_HTTP_PORT = os.environ.get("GITLAB_HTTP_PORT")

REPO_BRANCHES = os.environ.get("REPO_BRANCHES")
REPOS_PATH = os.environ.get("REPOS_PATH")
STATE_PATH = os.environ.get("STATE_PATH")

g = Github(GITHUB_ACCESS_TOKEN)

def get_key_content():
  try:
    with open(GITHUB_KEY_PATH, "r", encoding="utf-8") as key:
      return key.read()
  except Exception as error:
    print(error)

def add_github_key():
  response = requests.post(
    f"{GITHUB_API_URL}/user/keys",
    headers={
      "Accept": "application/vnd.github.v3+json",
      "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
    },
    json={
      "key": get_key_content(),
      "title": GITHUB_KEY_TITLE
    }
  )

  # Check if SSH key was created or has previously been registered.
  return (
    response.status_code == 201 or
    response.status_code == 422
  )

def format_full_name(full_name):
  return full_name.replace("/", "-", 1)

def add_remote(repo_path, repo_name):
  subprocess.call(
    f"cd {repo_path} && git remote add {GITLAB_REMOTE} ssh://git@{GITLAB_URL}:{GITLAB_SSH_PORT}/{GITLAB_HANDLE}/{repo_name}",
    shell=True
  )

def clone_repo(repo_path, ssh_url):
  subprocess.call(
    f"git clone {ssh_url} {repo_path}",
    shell=True
  )

def pull_repo(repo_path):
  subprocess.call(
    f"cd {repo_path} && git pull",
    shell=True
  )

def create_project(repo_name):
  response = requests.post(
    f"{GITLAB_URL_PROTOCOL}://{GITLAB_URL}:{GITLAB_HTTP_PORT}/api/v4/projects?name={repo_name}",
    headers={
      "PRIVATE-TOKEN": GITLAB_ACCESS_TOKEN
    }
  )

  if response.status_code == 201:
    print(f"{repo_name} project was succesfully created in GitLab.")
  elif response.status_code == 400:
    print(f"{repo_name} project has already been registered in GitLab.")
  else:
    raise Exception(f"API call for creating {repo_name} project failed in GitLab.")

def push_repo(repo_path):
  branches = REPO_BRANCHES.split(",")
  check_branch = "git rev-parse --verify"

  for index, branch in enumerate(branches):
    try:
      subprocess.check_output(
        f"cd {repo_path} && {check_branch} {branch}",
        stderr=subprocess.DEVNULL,
        shell=True,
      )
      subprocess.call(
        f"cd {repo_path} && git push --force {GITLAB_REMOTE} {branch}",
        stderr=subprocess.DEVNULL,
        shell=True,
      )
      print(f"{repo_path.replace(REPOS_PATH + '/', '')} was successfully pushed in Gitlab.")
      break
    except subprocess.CalledProcessError:
      if index == len(branches) - 1:
        print(f"Failed to push repo {repo_path}. Did not find default branch.")

state = {
  "is_github_key_added": False,
  "repos": {}
}

if os.path.isfile(STATE_PATH):
  with open(STATE_PATH, "r", encoding="utf-8") as jsonFile:
    state = json.load(jsonFile)

if state.get("is_github_key_added") != True:
  if add_github_key():
    state["is_github_key_added"] = True
  else:
    raise Exception("GitHub key was not added.")

# index = 0
for repo in g.get_user().get_repos():
  # index += 1
  full_name = format_full_name(repo.full_name)
  ssh_url = repo.ssh_url
  pushed_at = repo.pushed_at.timestamp()
  repo_path = os.path.join(REPOS_PATH, full_name)

  # if "gatsby" in repo_path:
  #   continue

  if not os.path.isdir(repo_path):
    print("Repo was not cloned.")
    clone_repo(repo_path, ssh_url)
    create_project(full_name)
    add_remote(repo_path, full_name)
  elif pushed_at > state["repos"][full_name]["updated"]:
    print("Repo was updated since the last download.")
    pull_repo(repo_path)

  if full_name not in state:
    state["repos"][full_name] = {}

  state["repos"][full_name]["updated"] = pushed_at

  push_repo(repo_path)

  # if index >= 20:
  #   break;

with open(STATE_PATH, "w", encoding="utf-8") as jsonFile:
  json.dump(state, jsonFile, indent=2)
