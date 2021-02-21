import os.path
import json
from dotenv import load_dotenv

load_dotenv()

STATE_PATH = os.environ.get("STATE_PATH")


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
        with open(STATE_PATH, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2)

    def read(self):
        if os.path.isfile(STATE_PATH):
            with open(STATE_PATH, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                self.is_github_key_added = data["is_github_key_added"]
                self.is_github_known_host = data["is_github_known_host"]
                self.is_gitlab_known_host = data["is_gitlab_known_host"]
                self.repos = data["repos"]
