import responses
import src.gitlab
from unittest import TestCase
from tests.get_mock import get_mock_content
from src.gitlab import (
    get_default_branch,
    get_repo_branches,
    create_gitlab_project
)
from src.enums import HttpStatusCode


class TestGitlab(TestCase):
    def test_get_default_branch(self):
        mock = get_mock_content("gitlab.json", "remote_branches")
        default_branch = get_default_branch(mock)
        self.assertEqual(default_branch, "master")

    def test_get_repo_branches(self):
        mock = get_mock_content("gitlab.json", "remote_branches")
        default_branch = get_repo_branches(mock)
        self.assertEqual(
            default_branch,
            [
                "featute/canvas-video-audio",
                "master",
                "renovate/feat/header",
                "renovate/configure",
                "my-awesome-slider"
            ]
        )

    @responses.activate
    def test_create_gitlab_project(self):
        GITLAB_URL_PROTOCOL = "https"
        GITLAB_URL = "gitlab.com"
        GITLAB_HTTP_PORT = "9080"
        GITLAB_ACCESS_TOKEN = "secret"
        gitlab_repo_name = "awesome-repo"

        gitlab_url = f"{GITLAB_URL_PROTOCOL}://{GITLAB_URL}:{GITLAB_HTTP_PORT}/api/v4/projects?name={gitlab_repo_name}"
        response_args_mock = {
            "method": responses.POST,
            "url": gitlab_url,
            "headers": {"PRIVATE-TOKEN": GITLAB_ACCESS_TOKEN}
        }

        responses.add(
            **response_args_mock,
            status=HttpStatusCode.CREATED.value
        )
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.BAD_REQUEST.value
        )
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.NOT_FOUND.value
        )

        src.gitlab.GITLAB_URL_PROTOCOL = GITLAB_URL_PROTOCOL
        src.gitlab.GITLAB_URL = GITLAB_URL
        src.gitlab.GITLAB_HTTP_PORT = GITLAB_HTTP_PORT
        src.gitlab.GITLAB_ACCESS_TOKEN = GITLAB_ACCESS_TOKEN

        self.assertEqual(
            create_gitlab_project(gitlab_repo_name),
            None
        )

        self.assertEqual(
            create_gitlab_project(gitlab_repo_name),
            None
        )

        with self.assertRaises(Exception):
            create_gitlab_project(gitlab_repo_name)
