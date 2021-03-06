import os
import subprocess
import requests
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


def get_default_branch(branches):
    for branch in branches:
        if "->" in branch:
            return branch.split("->")[1].split("/")[1].strip()


def get_repo_branches(branches):
    def filter_fn(branch): return branch.strip() and "->" not in branch
    def format_fn(branch): return "/".join(branch.strip().split("/")[1:])

    return list(map(format_fn, filter(filter_fn, branches)))


def push_gitlab_repo(repo_path):
    remote_branches = subprocess.check_output(
        f"cd {repo_path} && \
        git branch --remote",
        shell=True
    ).decode("utf-8").split("\n")

    default_branch = get_default_branch(remote_branches)
    branches = get_repo_branches(remote_branches)

    for branch in branches:
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
        raise Exception(
            f"API call for creating {repo_name} project failed in GitLab.")


def add_gitlab_remote(repo_path, repo_name):
    ssh_url = f"ssh://git@{GITLAB_URL}:{GITLAB_SSH_PORT}/{GITLAB_HANDLE}/{repo_name}"
    subprocess.call(
        f"cd {repo_path} && \
        git remote add {GITLAB_REMOTE} {ssh_url}",
        shell=True
    )
