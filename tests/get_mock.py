import os
from json import loads

MOCKS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "mocks"
)


def get_mock_content(file_name, key):
    path = os.path.join(MOCKS_PATH, file_name)
    with open(path, "r", encoding="utf-8") as content:
        if key:
            return loads(content.read())[key]
        return content.read()
