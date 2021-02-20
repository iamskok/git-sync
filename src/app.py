import os.path
from time import sleep
from github import Github
from dotenv import load_dotenv
from .logger import create_logger
from .state import State
from .github_rate_limiter import GithubRateLimiter
from .github import pull_github_repo, add_github_key, clone_github_repo
from .gitlab import push_gitlab_repo, create_gitlab_project, add_gitlab_remote
from .utils import format_full_name, add_known_host, is_repo_blacklisted

load_dotenv()

GITHUB_URL = os.environ.get("GITHUB_URL")
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITLAB_URL = os.environ.get("GITLAB_URL")
GITLAB_SSH_PORT = os.environ.get("GITLAB_SSH_PORT")
REPOS_PATH = os.environ.get("REPOS_PATH")
SYNC_TIME = os.environ.get("SYNC_TIME")

g = Github(GITHUB_ACCESS_TOKEN)

logger = create_logger()

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
        push_gitlab_repo(repo_path)
        state.update_repo(full_name, "is_pushed_to_gitlab")

def run():
  while True:
    git_sync()
    if (SYNC_TIME):
      sleep(int(SYNC_TIME))
    else:
      break
