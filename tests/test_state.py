import os
from json import loads
from unittest import TestCase
from unittest.mock import patch
import src
from src.state import State
from tests.get_mock import get_mock_content, MOCKS_PATH


state_mock_path = os.path.join(MOCKS_PATH, "state.json")


class TestState(TestCase):
    def test_initial_state(self):
        state = State(read=False)
        mocked_state = get_mock_content("state.json", "initial")
        self.assertEqual(state.__dict__, mocked_state)

    read_state = get_mock_content("state.json", "read")

    @patch(
        "json.loads",
        lambda *args, **kwargs: get_mock_content("state.json", "read")
    )
    def test_read(self):
        src.state.STATE_PATH = state_mock_path
        state = State()
        state.read()
        self.assertEqual(state.__dict__, self.read_state)

    @patch(
        "json.loads",
        lambda *args, **kwargs: get_mock_content("state.json", "write")
    )
    def test_write(self):
        write_state_path = os.path.join(MOCKS_PATH, "write_state.json")

        src.state.STATE_PATH = state_mock_path
        state = State()

        src.state.STATE_PATH = write_state_path
        state.write()

        with open(write_state_path, "r", encoding="utf-8") as written_state:
            self.assertEqual(
                state.__dict__,
                loads(written_state.read())
            )
            os.remove(write_state_path)

    @patch(
        "json.loads",
        lambda *args, **kwargs: get_mock_content("state.json", "get_repo_attr")
    )
    def test_get_repo_attr(self):
        src.state.STATE_PATH = state_mock_path
        state = State()
        self.assertEqual(
            state.get_repo_attr("repo-1", "is_gitlab_project_created"),
            True
        )
        self.assertEqual(
            state.get_repo_attr("non_existing_repo",
                                "is_gitlab_project_created"),
            None
        )
        self.assertEqual(
            state.get_repo_attr("repo-1", "non_existing_repo_attribute"),
            None
        )
