import os.path
import json
import subprocess
import requests
from time import sleep, time
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITHUB_HANDLE = os.environ.get("GITHUB_HANDLE")
GITHUB_KEY_TITLE = os.environ.get("GITHUB_KEY_TITLE")
GITHUB_KEY_PATH = os.environ.get("GITHUB_KEY_PATH")
GITHUB_URL = os.environ.get("GITHUB_URL")
GITHUB_API_URL = os.environ.get("GITHUB_API_URL")
GITHUB_RATE_LIMIT = os.environ.get("GITHUB_RATE_LIMIT")

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
KNOWN_HOSTS_PATH = os.environ.get("KNOWN_HOSTS_PATH")
SYNC_TIME = os.environ.get("SYNC_TIME")

g = Github(GITHUB_ACCESS_TOKEN)

def get_ssh_key_content():
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
      "key": get_ssh_key_content(),
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

def add_known_host(host):
  # Handle custom port case
  if len(host.split(":")) == 2:
    _host = host.split(':')[0]
    _port = host.split(':')[1]
    subprocess.call(
      f"ssh-keyscan -p {_port} -H {_host} >> {KNOWN_HOSTS_PATH}",
      shell=True
    )
  else:
    subprocess.call(
      f"ssh-keyscan -H {host} >> {KNOWN_HOSTS_PATH}",
      shell=True
    )

def add_gitlab_remote(repo_path, repo_name):
  subprocess.call(
    f"cd {repo_path} && git remote add {GITLAB_REMOTE} ssh://git@{GITLAB_URL}:{GITLAB_SSH_PORT}/{GITLAB_HANDLE}/{repo_name}",
    shell=True
  )

def clone_github_repo(repo_path, ssh_url):
  subprocess.call(
    f"git clone {ssh_url} {repo_path}",
    shell=True
  )

def pull_github_repo(repo_path):
  subprocess.call(
    f"cd {repo_path} && git pull",
    shell=True
  )

def create_gitlab_project(repo_name):
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

class GithubLimitsException(Exception):
  pass

class GithubRateLimiter:
  def __init__(self):
    self.reset_timestamp = None
    self.remaining = None
    self.init_limits()

  def init_limits(self):
    response = requests.get(
      f"{GITHUB_API_URL}/rate_limit",
      headers={
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
      }
    )
    if response.status_code == 200:
      rate_limit = response.json()["resources"]["core"]
      self.reset_timestamp = rate_limit["reset"]
      self.remaining = rate_limit["remaining"]
    else:
      raise GithubLimitsException(f"{GITHUB_API_URL}/rate_limit returned non 200 status code")

  def update_remaining(self):
    if self.remaining > 0:
      self.remaining -= 1
    else:
      t1 = self.reset_timestamp
      t2 = time()
      delta_t = t1 - t2
      if delta_t > 0:
        sleep(delta_t)
      self.init_limits()


def git_sync():
  gh_limiter = GithubRateLimiter()

  state = {
    "is_github_key_added": False,
    "is_github_known_host": False,
    "is_gitlab_known_host": False,
    "repos": {}
  }

  if os.path.isfile(STATE_PATH):
    with open(STATE_PATH, "r", encoding="utf-8") as jsonFile:
      state = json.load(jsonFile)

  if state.get("is_github_key_added") != True:
    if add_github_key():
      state["is_github_key_added"] = True
      gh_limiter.update_remaining()
    else:
      raise Exception("GitHub key was not added.")

  if state.get("is_github_known_host") != True:
    add_known_host(GITHUB_URL)
    state["is_github_known_host"] = True

  if state.get("is_gitlab_known_host") != True:
    add_known_host(f"{GITLAB_URL}:{GITLAB_SSH_PORT}")
    state["is_gitlab_known_host"] = True

  index = 0
  for repo in g.get_user().get_repos():
    gh_limiter.update_remaining()

    full_name = format_full_name(repo.full_name)
    ssh_url = repo.ssh_url
    pushed_at = repo.pushed_at.timestamp()
    repo_path = os.path.join(REPOS_PATH, full_name)

    if not os.path.isdir(repo_path):
      print("Repo was not cloned.")
      clone_github_repo(repo_path, ssh_url)
      create_gitlab_project(full_name)
      add_gitlab_remote(repo_path, full_name)
    elif pushed_at > state["repos"][full_name]["updated"]:
      print("Repo was updated since the last download.")
      pull_github_repo(repo_path)

    if full_name not in state:
      state["repos"][full_name] = {}

    state["repos"][full_name]["updated"] = pushed_at

    push_repo(repo_path)

    with open(STATE_PATH, "w", encoding="utf-8") as jsonFile:
      json.dump(state, jsonFile, indent=2)

while True:
  git_sync()
  sleep(int(SYNC_TIME))
