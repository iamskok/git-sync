import responses
import src.github
from unittest import TestCase
from src.github import is_github_key_added
from src.enums import HttpStatusCode


class TestGithub(TestCase):
    @responses.activate
    def test_is_github_key_added(self):
        GITHUB_API_URL = "https://api.github.com"
        GITHUB_ACCESS_TOKEN = "secret"
        GITHUB_KEY_TITLE = "new-ssh-key"
        SSH_KEY_CONTENT = "ssh-key-content"

        githab_url = f"{GITHUB_API_URL}/user/keys"
        response_args_mock = {
            "method": responses.POST,
            "url": githab_url,
            "headers": {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
            },
            "json": {
                "key": SSH_KEY_CONTENT,
                "title": GITHUB_KEY_TITLE
            },
        }
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.CREATED.value
        )
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.UNPROCESSABLE_ENTITY.value
        )
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.NOT_FOUND.value
        )

        src.github.GITHUB_API_URL = GITHUB_API_URL
        src.github.GITHUB_ACCESS_TOKEN = GITHUB_ACCESS_TOKEN
        src.github.GITHUB_KEY_TITLE = GITHUB_KEY_TITLE
        src.github.get_ssh_key_content = lambda: SSH_KEY_CONTENT

        self.assertEqual(
            is_github_key_added(),
            True
        )
        self.assertEqual(
            is_github_key_added(),
            True
        )
        self.assertEqual(
            is_github_key_added(),
            False
        )
