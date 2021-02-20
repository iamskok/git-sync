import os.path
import requests
from time import sleep, time
from dotenv import load_dotenv
from .enums import HttpStatusCode

load_dotenv()

GITHUB_API_URL = os.environ.get("GITHUB_API_URL")
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")

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
    if response.status_code == HttpStatusCode.OK.value:
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
