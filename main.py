import os.path
import json
import subprocess
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
REPOS_PATH = os.environ.get("REPOS_PATH")
GITHUB_HANDLE = os.environ.get("GITHUB_HANDLE")
GITLAB_HANDLE = os.environ.get("GITLAB_HANDLE")
GITLAB_REMOTE = os.environ.get("GITLAB_REMOTE")
GITLAB_URL = os.environ.get("GITLAB_URL")
GITLAB_SSH_PORT = os.environ.get("GITLAB_SSH_PORT")
GITLAB_HTTP_PORT = os.environ.get("GITLAB_HTTP_PORT")
STATE_PATH = os.environ.get("STATE_PATH")

g = Github(GITHUB_ACCESS_TOKEN)

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
  try:
    request = f'curl --header "PRIVATE-TOKEN: {GITLAB_ACCESS_TOKEN}" -X POST "http://{GITLAB_URL}:{GITLAB_HTTP_PORT}/api/v4/projects?name={repo_name}"'
    subprocess.call(request, shell=True)
  except Exception as error:
    print("Gitlab create project API call failed.")
    print(error)

def push_repo(repo_path):
  branches = ["main", "master"]
  check_branch = "git rev-parse --verify"

  for index, branch in enumerate(branches):
    try:
      subprocess.check_output(f"cd {repo_path} && {check_branch} {branch}", shell=True)
      subprocess.call(
        f"cd {repo_path} && git push {GITLAB_REMOTE} {branch}",
        shell=True
      )
      print(f"Repo was successfully pushed in Gitlab. {repo_path}")
      break
    except subprocess.CalledProcessError:
      if index == len(branches) - 1:
        print(f"Failed to push repo {repo_path}. Did not find default branch.")

state = {}

if os.path.isfile(STATE_PATH):
  with open(STATE_PATH, "r", encoding="utf-8") as jsonFile:
    state = json.load(jsonFile)

index = 0
for repo in g.get_user().get_repos():
  index += 1
  full_name = format_full_name(repo.full_name)
  ssh_url = repo.ssh_url
  pushed_at = repo.pushed_at.timestamp()
  repo_path = os.path.join(REPOS_PATH, full_name)

  if "gatsby" in repo_path:
    continue

  if not os.path.isdir(repo_path):
    print("Repo was not cloned.")
    clone_repo(repo_path, ssh_url)
    create_project(full_name)
    add_remote(repo_path, full_name)
  elif pushed_at > state[full_name]["updated"]:
    print("Repo was updated since the last download.")
    pull_repo(repo_path)

  if full_name not in state:
    state[full_name] = {}

  state[full_name]["updated"] = pushed_at

  push_repo(repo_path)

  if index == 5:
    break;

with open(STATE_PATH, "w", encoding="utf-8") as jsonFile:
  json.dump(state, jsonFile, indent=2)
