import os
import subprocess
import requests
from dotenv import load_dotenv
from .enums import HttpStatusCode
from .utils import get_ssh_key_content

load_dotenv()

GITHUB_API_URL = os.environ.get("GITHUB_API_URL")
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITHUB_KEY_TITLE = os.environ.get("GITHUB_KEY_TITLE")


def pull_github_repo(repo_path):
  subprocess.call(
    f"cd {repo_path} && \
      git fetch --all && \
      git pull",
    shell=True
  )

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
  
  return (
    response.status_code == HttpStatusCode.CREATED.value or
    response.status_code == HttpStatusCode.UNPROCESSABLE_ENTITY.value
  )

def clone_github_repo(repo_path, ssh_url):
  subprocess.call(
    f"git clone {ssh_url} {repo_path}",
    shell=True
  )