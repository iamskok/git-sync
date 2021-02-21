import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

GITHUB_KEY_PATH = os.environ.get("GITHUB_KEY_PATH")
KNOWN_HOSTS_PATH = os.environ.get("KNOWN_HOSTS_PATH")
REPOS_BLACKLIST = os.environ.get("REPOS_BLACKLIST")


def get_ssh_key_content():
    if os.path.isfile(GITHUB_KEY_PATH):
        with open(GITHUB_KEY_PATH, "r", encoding="utf-8") as key:
            content = key.read()

            is_valid_key = "is not a public key file." not in subprocess.check_output(
                f"ssh-keygen -l -f {GITHUB_KEY_PATH}",
                shell=True
            ).decode("utf-8")

            if is_valid_key:
                return content

            raise Exception(
                f"{GITHUB_KEY_PATH} SSH public key has invalid format")
    else:
        raise Exception(f"{GITHUB_KEY_PATH} file path does not exist.")


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
    return repo in blacklist.split(",")
