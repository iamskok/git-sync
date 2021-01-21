from github import Github
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
SSH_URL = "git@github.com"

g = Github(GITHUB_ACCESS_TOKEN)

for repo in g.get_user().get_repos():
  ssh_url = f"{SSH_URL}:{repo.full_name}"
  subprocess.call(f"git clone {ssh_url}", shell=True)
  print(repo.full_name)
