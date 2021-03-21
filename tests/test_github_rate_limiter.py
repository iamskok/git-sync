import responses
from time import time
from unittest import TestCase
import src
from src.github_rate_limiter import GithubRateLimiter, GithubLimitsError
from src.enums import HttpStatusCode
from tests.get_mock import get_mock_content

GITHUB_API_URL = "https://api.github.com"
GITHUB_ACCESS_TOKEN = "secret"
github_url = f"{GITHUB_API_URL}/rate_limit"
response_args_mock = {
    "method": responses.GET,
    "url": github_url,
    "headers": {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
    }
}

src.github_rate_limiter.GithubRateLimiter.GITHUB_API_URL = GITHUB_API_URL
src.github_rate_limiter.GithubRateLimiter.GITHUB_ACCESS_TOKEN = GITHUB_ACCESS_TOKEN

class TestState(TestCase):
    @responses.activate
    def test_init_limits(self):
        for _ in range(2):
            responses.add(
                **response_args_mock,
                status=HttpStatusCode.OK.value,
                json=get_mock_content("github_rate_limiter.json")
            )
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.BAD_REQUEST.value
        )

        github_rate_limiter = GithubRateLimiter()
        github_rate_limiter.init_limits()

        self.assertEqual(
            github_rate_limiter.reset_timestamp,
            1616274801
        )

        self.assertEqual(
            github_rate_limiter.remaining,
            4754
        )

        with self.assertRaises(GithubLimitsError):
            github_rate_limiter.init_limits()

    @responses.activate
    def test_update_remaining(self):
        responses.add(
            **response_args_mock,
            status=HttpStatusCode.OK.value,
            json=get_mock_content("github_rate_limiter.json")
        )

        github_rate_limiter = GithubRateLimiter()
        github_rate_limiter.update_remaining()

        self.assertEqual(
            github_rate_limiter.remaining,
            4754 - 1,
        )

        github_rate_limiter.remaining = 0
        github_rate_limiter.reset_timestamp = time()
        github_rate_limiter.update_remaining()

        self.assertEqual(
            github_rate_limiter.remaining,
            4754,
        )
