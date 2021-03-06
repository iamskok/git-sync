import os
import re
import subprocess
from subprocess import CalledProcessError
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
    return re.sub(r"\/|\.", "-", full_name)


class InvalidHostError(Exception):
    pass


def add_known_host(host):
    # Handle custom port case
    try:
        if host.find(":") > -1:
            host, port, *_ = host.split(":")
            output = subprocess.check_output(
                f"ssh-keyscan -p {port} -H {host} >> {KNOWN_HOSTS_PATH}",
                shell=True,
                stderr=subprocess.STDOUT
            )
        else:
            output = subprocess.check_output(
                f"ssh-keyscan -H {host} >> {KNOWN_HOSTS_PATH}",
                shell=True,
                stderr=subprocess.STDOUT
            )

        # Exception is thrown when status code is not equal to `0`.
        # Linux `ssh-keyscan` does not throw Exception so we are checking its output message instead
        if "not known" in output.decode('utf-8'):
            raise CalledProcessError(1, "ssh-keyscan")

    # MacOS `ssh-keyscan` throws Exception
    except CalledProcessError:
        raise InvalidHostError(f"Invalid host name {host}")


def is_repo_blacklisted(repo, blacklist=REPOS_BLACKLIST):
    return False if blacklist is None else repo in blacklist.split(",")


def fix_ssh_private_key(string):
    pattern = re.compile(r"(\-+[A-Z\s]+\-+)", flags=re.DOTALL)
    begin_string, end_string = pattern.findall(string)

    new_key = re.sub(begin_string, "", string)
    new_key = re.sub(end_string, "", new_key)
    new_key = re.sub(" ", "\n", new_key.strip())
    new_key = f"{begin_string}\n{new_key}\n{end_string}\n"

    return new_key


def rewrite_ssh_private_key(key_path):
    """
        Fixes new line issue with env variables
        in `CMD` directive of Dockerfile.

        - preserves begin and end strings
        - replaces all instances of whitespace with new lines
        - replaces the content of the original private key SSH file
    """

    with open(key_path, "r", encoding="utf-8") as key:
        content = key.read()
        new_key = fix_ssh_private_key(content)

    with open(key_path, "w", encoding="utf-8") as key_file:
        key_file.write(new_key)
