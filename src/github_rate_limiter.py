import os.path
from time import sleep, time
from dotenv import load_dotenv
import requests
from .enums import HttpStatusCode

load_dotenv()

GITHUB_API_URL = os.environ.get("GITHUB_API_URL")
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")


class GithubLimitsError(Exception):
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
            raise GithubLimitsError(
                f"{GITHUB_API_URL}/rate_limit returned non 200 status code")

    def update_remaining(self):
        if self.remaining > 0:
            self.remaining -= 1
        else:
            timestamp_1 = self.reset_timestamp
            timestamp_2 = time()
            time_delta = timestamp_1 - timestamp_2
            if time_delta > 0:
                sleep(time_delta)
            self.init_limits()
