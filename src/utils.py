import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

GITHUB_KEY_PATH = os.environ.get("GITHUB_KEY_PATH")
KNOWN_HOSTS_PATH = os.environ.get("KNOWN_HOSTS_PATH")
REPOS_BLACKLIST = os.environ.get("REPOS_BLACKLIST")


class InvalidSSHKeyError(Exception):
    pass


def get_ssh_key_content():
    if os.path.isfile(GITHUB_KEY_PATH):
        with open(GITHUB_KEY_PATH, "r", encoding="utf-8") as key:
            content = key.read()

            exit_code = subprocess.call(
                f"ssh-keygen -l -f {GITHUB_KEY_PATH}",
                shell=True
            )

            if exit_code != 0:
                raise InvalidSSHKeyError(
                    f"Invalid SSH key. `ssh-keygen` returned non zero exit code - {exit_code}"
                )

            return content
    else:
        raise FileNotFoundError(f"{GITHUB_KEY_PATH} file path does not exist.")


def format_full_name(full_name):
    return full_name.replace("/", "-", 1)


class InvalidHostError(Exception):
    pass


def add_known_host(host):
    # Handle custom port case
    if host.find(":") > -1:
        host, port, *_ = host.split(":")
        exit_code = subprocess.call(
            f"ssh-keyscan -p {port} -H {host} >> {KNOWN_HOSTS_PATH}",
            shell=True
        )
    else:
        exit_code = subprocess.call(
            f"ssh-keyscan -H {host} >> {KNOWN_HOSTS_PATH}",
            shell=True
        )

    if exit_code != 0:
        raise InvalidHostError(f"Invalid host name {host}")


def is_repo_blacklisted(repo, blacklist=REPOS_BLACKLIST):
    return False if blacklist is None else repo in blacklist.split(",")
