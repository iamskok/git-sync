import os
import unittest
from unittest import TestCase, mock
import src.utils
from src.utils import (
    format_full_name,
    get_ssh_key_content,
    InvalidSSHKeyError,
    add_known_host,
    InvalidHostError,
    is_repo_blacklisted,
    fix_ssh_private_key,
)

# class FormatFullName(TestCase):
#     def test_format_full_name(self):
#         self.assertEqual(format_full_name("facebook/react"), "facebook-react")
#         self.assertEqual(format_full_name(
#             "username/example.com"), "username-example-com")


# class GetSSHKeyContent(TestCase):
#     dir_path = os.path.dirname(os.path.realpath(__file__))

#     @mock.patch.dict(os.environ, {
#         "GITHUB_KEY_PATH": os.path.join(
#             dir_path,
#             "mocks",
#             "valid_ssh_public_key"
#         )
#     })
#     def test_valid_ssh_key(self):
#         src.utils.GITHUB_KEY_PATH = os.environ["GITHUB_KEY_PATH"]
#         with open(
#             src.utils.GITHUB_KEY_PATH,
#             "r",
#             encoding="utf-8"
#         ) as ssh_key_file_content:
#             self.assertEqual(
#                 get_ssh_key_content(),
#                 ssh_key_file_content.read()
#             )

#     @mock.patch.dict(os.environ, {
#         "GITHUB_KEY_PATH": os.path.join(
#             dir_path,
#             "mocks",
#             "invalid_ssh_public_key"
#         )
#     })
#     def test_invalid_ssh_key(self):
#         src.utils.GITHUB_KEY_PATH = os.environ["GITHUB_KEY_PATH"]
#         self.assertRaises(
#             InvalidSSHKeyError,
#             get_ssh_key_content,
#         )

#     @mock.patch.dict(os.environ, {
#         "GITHUB_KEY_PATH": os.path.join(
#             dir_path,
#             "mocks",
#             "non_existing_public_ssh_key"
#         )
#     })
#     def test_non_existing_ssh_key(self):
#         src.utils.GITHUB_KEY_PATH = os.environ["GITHUB_KEY_PATH"]
#         self.assertRaises(
#             FileNotFoundError,
#             get_ssh_key_content,
#         )


# class AddKnownHost(TestCase):
#     def test_add_host(self):
#         self.assertEqual(add_known_host("github.com"), None)

#     def test_add_host_and_port(self):
#         self.assertEqual(add_known_host("github.com:22"), None)

#     def test_invalid_host(self):
#         self.assertRaises(
#             InvalidHostError,
#             lambda: add_known_host("nonexistinghost123456789123456789.com"),
#         )


# class IsRepoBlacklisted(TestCase):
#     blacklist = "facebook/react,nodejs/node,gorilla/websocket"

#     def test_blacklisted_repo(self):
#         self.assertEqual(is_repo_blacklisted(
#             "facebook/react", self.blacklist), True)

#     def test_non_blacklisted_repo(self):
#         self.assertEqual(is_repo_blacklisted(
#             "gatsbyjs/gatsby", self.blacklist), False)

#     def test_undefined_blacklist(self):
#         self.assertEqual(is_repo_blacklisted("gatsbyjs/gatsby", None), False)

class FixSshPrivateKey(TestCase):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    malformed_ssh_private_key_path = os.path.join(
        dir_path,
        "mocks",
        "malformed_ssh_private_key"
    )
    valid_ssh_private_key_path = os.path.join(
        dir_path,
        "mocks",
        "valid_ssh_private_key"
    )

    def test_fix_ssh_private_key(self):
        with open(self.malformed_ssh_private_key_path, "r", encoding="utf-8") as malformed_key:
            with open(self.valid_ssh_private_key_path, "r", encoding="utf-8") as valid_key:
                self.assertEqual(
                    fix_ssh_private_key(malformed_key.read()),
                    valid_key.read()
                )


if __name__ == '__main__':
    unittest.main()
