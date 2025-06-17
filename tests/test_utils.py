import unittest
from configparser import RawConfigParser
from unittest import mock

from scripts import utils


class TestUtils(unittest.TestCase):

    @mock.patch("scripts.utils.os.environ", {"GITHUB_REPOSITORY": "cvilbrandt/tamberlane"})
    def test_get_comic_url_on_github(self):
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Settings")
        # No domain or subdirectory set
        self.assertEqual(
            ("https://cvilbrandt.github.io/tamberlane", "/tamberlane"),
            utils.get_comic_url(comic_info)
        )
        # With https:// and empty subdirectory
        comic_info.set("Comic Settings", "Comic domain", "https://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://www.tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
        # With https:// and nonempty subdirectory
        comic_info.set("Comic Settings", "Comic domain", "https://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "my_comic")
        self.assertEqual(
            ("https://www.tamberlanecomic.com/my_comic", "/my_comic"),
            utils.get_comic_url(comic_info)
        )
        # With http://
        comic_info.set("Comic Settings", "Comic domain", "http://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://www.tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
        # With no http://
        comic_info.set("Comic Settings", "Comic domain", "tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
        # With no http://, and don't force use https
        comic_info.set("Comic Settings", "Comic domain", "tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        comic_info.set("Comic Settings", "Use https when building comic URL", "False")
        self.assertEqual(
            ("https://tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
        # With no http://, and force use https
        comic_info.set("Comic Settings", "Comic domain", "tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        comic_info.set("Comic Settings", "Use https when building comic URL", "True")
        self.assertEqual(
            ("https://tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )

    @mock.patch("scripts.utils.os.environ", {"GITHUB_REPOSITORY": "cvilbrandt/tamberlane"})
    @mock.patch("scripts.utils.os.path.isfile", return_value=True)
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="tamberlanecomic.com")
    def test_get_comic_url_with_cname(self, *m):
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Settings")
        # No domain or subdirectory set
        self.assertEqual(
            ("https://tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
        # With https:// and empty subdirectory
        comic_info.set("Comic Settings", "Comic domain", "https://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://www.tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )

    @mock.patch("scripts.utils.os.environ", {"GITHUB_REPOSITORY": "cvilbrandt/cvilbrandt.github.io"})
    def test_get_comic_url_on_github_special_repo_name(self):
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Settings")
        # No domain or subdirectory set
        self.assertEqual(
            ("https://cvilbrandt.github.io", ""),
            utils.get_comic_url(comic_info)
        )
        # With https:// and empty subdirectory
        comic_info.set("Comic Settings", "Comic domain", "https://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://www.tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )

    @mock.patch("scripts.utils.os.environ", {})
    def test_get_comic_url_local(self):
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Settings")
        # No domain or subdirectory set
        with self.assertRaises(ValueError):
            utils.get_comic_url(comic_info)
        # With https:// and empty subdirectory
        comic_info.set("Comic Settings", "Comic domain", "https://www.tamberlanecomic.com")
        comic_info.set("Comic Settings", "Comic subdirectory", "")
        self.assertEqual(
            ("https://www.tamberlanecomic.com", ""),
            utils.get_comic_url(comic_info)
        )
