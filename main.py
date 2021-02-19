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

GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
GITLAB_HANDLE = os.environ.get("GITLAB_HANDLE")
GITLAB_REMOTE = os.environ.get("GITLAB_REMOTE")
GITLAB_URL = os.environ.get("GITLAB_URL")
GITLAB_URL_PROTOCOL = os.environ.get("GITLAB_URL_PROTOCOL")
GITLAB_SSH_PORT = os.environ.get("GITLAB_SSH_PORT")
GITLAB_HTTP_PORT = os.environ.get("GITLAB_HTTP_PORT")

REPOS_PATH = os.environ.get("REPOS_PATH")
REPOS_BLACKLIST = os.environ.get("REPOS_BLACKLIST")
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
    _host = host.split(":")[0]
    _port = host.split(":")[1]
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
    f"cd {repo_path} && \
      git remote add {GITLAB_REMOTE} ssh://git@{GITLAB_URL}:{GITLAB_SSH_PORT}/{GITLAB_HANDLE}/{repo_name}",
    shell=True
  )

def clone_github_repo(repo_path, ssh_url):
  subprocess.call(
    f"git clone {ssh_url} {repo_path}",
    shell=True
  )

def pull_github_repo(repo_path):
  subprocess.call(
    f"cd {repo_path} && \
      git fetch --all && \
      git pull",
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
  all_remote_branches = subprocess.check_output(
    f"cd {repo_path} && \
      git branch --remote",
    shell=True
  ).decode("utf-8").split("\n")

  default_branch = [branch.split("->")[1].split("/")[1].strip() for branch in all_remote_branches if "->" in branch][0]
  all_remote_branches = [branch.strip().split("/")[1] for branch in all_remote_branches if branch.strip() and "->" not in branch]

  for branch in all_remote_branches:
    subprocess.call(
      f"cd {repo_path} && \
        git fetch --all && \
        git checkout {'-b' if branch != default_branch else ''} {branch} -- && \
        git push --force {GITLAB_REMOTE} {branch}",
      stderr=subprocess.DEVNULL,
      shell=True,
    )

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


class State():
  def __init__(self):
    self.is_github_key_added = False
    self.is_github_known_host = False
    self.is_gitlab_known_host = False
    self.repos = {}
    self.read()

  def get_repo_attr(self, name, attr):
    if self.repos.get(name) is None or self.repos[name].get(attr) is None:
      return None

    return self.repos[name][attr]

  def update(self, key, value=True):
    self.__dict__[key] = value
    self.write()

  def update_repo(self, name, key, value=True):
    if name not in self.repos:
      self.repos[name] = {}

    self.repos[name][key] = value
    self.write()

  def write(self):
    data = {
      "is_github_key_added": self.is_github_key_added,
      "is_github_known_host": self.is_github_known_host,
      "is_gitlab_known_host": self.is_gitlab_known_host,
      "repos": self.repos,
    }
    with open(STATE_PATH, "w", encoding="utf-8") as jsonFile:
      json.dump(data, jsonFile, indent=2)

  def read(self):
    if os.path.isfile(STATE_PATH):
      with open(STATE_PATH, "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)
        self.is_github_key_added = data["is_github_key_added"]
        self.is_github_known_host = data["is_github_known_host"]
        self.is_gitlab_known_host = data["is_gitlab_known_host"]
        self.repos = data["repos"]

def is_repo_blacklisted(repo, blacklist=REPOS_BLACKLIST):
  return True if repo in blacklist.split(",") else False

def git_sync():
  state = State()
  gh_limiter = GithubRateLimiter()

  if state.is_github_key_added != True:
    if add_github_key():
      state.update("is_github_key_added")
      gh_limiter.update_remaining()
    else:
      raise Exception("GitHub key was not added.")

  if state.is_github_known_host != True:
    add_known_host(GITHUB_URL)
    state.update("is_github_known_host")

  if state.is_gitlab_known_host != True:
    add_known_host(f"{GITLAB_URL}:{GITLAB_SSH_PORT}")
    state.update("is_gitlab_known_host")

  for repo in g.get_user().get_repos():
    gh_limiter.update_remaining()
    name = repo.full_name

    if not is_repo_blacklisted(name):
      full_name = format_full_name(name)
      ssh_url = repo.ssh_url
      pushed_at = repo.pushed_at.timestamp()
      repo_path = os.path.join(REPOS_PATH, full_name)

      if not os.path.isdir(repo_path):
        print("Repo was not cloned.")
        clone_github_repo(repo_path, ssh_url)
        if state.get_repo_attr(full_name, "is_gitlab_project_created") != True:
          create_gitlab_project(full_name)
          state.update_repo(full_name, "is_gitlab_project_created")

        if state.get_repo_attr(full_name, "is_gitlab_remote_created") != True:
          add_gitlab_remote(repo_path, full_name)
          state.update_repo(full_name, "is_gitlab_remote_created")

      elif pushed_at > state.get_repo_attr(full_name, "updated"):
        print("Repo was updated since the last download.")
        pull_github_repo(repo_path)
        state.update_repo(full_name, "is_pushed_to_gitlab", False)

      state.update_repo(full_name, "updated", pushed_at)

      if state.get_repo_attr(full_name, "is_pushed_to_gitlab") != True:
        push_repo(repo_path)
        state.update_repo(full_name, "is_pushed_to_gitlab")

while True:
  git_sync()
  sleep(int(SYNC_TIME))
