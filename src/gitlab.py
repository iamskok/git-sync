import os
import requests
import subprocess
from dotenv import load_dotenv
from .enums import HttpStatusCode

load_dotenv()

GITLAB_REMOTE = os.environ.get("GITLAB_REMOTE")
GITLAB_URL = os.environ.get("GITLAB_URL")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
GITLAB_HTTP_PORT = os.environ.get("GITLAB_HTTP_PORT")
GITLAB_URL_PROTOCOL = os.environ.get("GITLAB_URL_PROTOCOL")
GITLAB_SSH_PORT = os.environ.get("GITLAB_SSH_PORT")
GITLAB_HANDLE = os.environ.get("GITLAB_HANDLE")

def push_gitlab_repo(repo_path):
  all_remote_branches = subprocess.check_output(
    f"cd {repo_path} && \
      git branch --remote",
    shell=True
  ).decode("utf-8").split("\n")

  default_branch = [
    branch.split("->")[1].split("/")[1].strip()
    for branch in all_remote_branches
    if "->" in branch
  ][0]
  all_remote_branches = [
    branch.strip().split("/")[1]
    for branch in all_remote_branches
    if branch.strip() and "->" not in branch
  ]

  for branch in all_remote_branches:
    command = " && ".join([
      f"cd {repo_path}",
      "git fetch --all",
      # `branch --` explicitly selects branch rather than file name.
      f"git checkout {'-b' if branch != default_branch else ''} {branch} --",
      f"git push --force {GITLAB_REMOTE} {branch}",
    ])
    subprocess.call(
      command,
      stderr=subprocess.DEVNULL,
      shell=True,
    )

def create_gitlab_project(repo_name):
  response = requests.post(
    f"{GITLAB_URL_PROTOCOL}://{GITLAB_URL}:{GITLAB_HTTP_PORT}/api/v4/projects?name={repo_name}",
    headers={
      "PRIVATE-TOKEN": GITLAB_ACCESS_TOKEN
    }
  )

  if response.status_code == HttpStatusCode.CREATED.value:
    print(f"{repo_name} project was succesfully created in GitLab.")
  elif response.status_code == HttpStatusCode.BAD_REQUEST.value:
    print(f"{repo_name} project has already been registered in GitLab.")
  else:
    raise Exception(f"API call for creating {repo_name} project failed in GitLab.")

def add_gitlab_remote(repo_path, repo_name):
  ssh_url = f"ssh://git@{GITLAB_URL}:{GITLAB_SSH_PORT}/{GITLAB_HANDLE}/{repo_name}"
  subprocess.call(
    f"cd {repo_path} && \
      git remote add {GITLAB_REMOTE} {ssh_url}",
    shell=True
  )
