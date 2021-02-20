import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

GITHUB_KEY_PATH = os.environ.get("GITHUB_KEY_PATH")
KNOWN_HOSTS_PATH = os.environ.get("KNOWN_HOSTS_PATH")
REPOS_BLACKLIST = os.environ.get("REPOS_BLACKLIST")

def get_ssh_key_content():
  try:
    with open(GITHUB_KEY_PATH, "r", encoding="utf-8") as key:
      return key.read()
  except Exception as error:
    print(error)

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

def is_repo_blacklisted(repo, blacklist=REPOS_BLACKLIST):
  return True if repo in blacklist.split(",") else False
