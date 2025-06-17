from configparser import RawConfigParser
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
from xml.etree import ElementTree

from scripts import build_rss_feed


class TestRssFeed(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comic_info = RawConfigParser()
        cls.comic_info.add_section("Comic Info")
        cls.comic_info.set("Comic Info", "Comic name", "The Dark World of the Furry")
        cls.comic_info.set("Comic Info", "Author", "Lucifer, Prince of Lies")
        cls.comic_info.add_section("Comic Settings")
        cls.comic_info.set("Comic Settings", "Date format", "%B %d, %Y")
        cls.comic_info.set("Comic Settings", "Comic domain", "www.tamberlanecomic.com")
        cls.comic_info.set("Comic Settings", "Comic subdirectory", "")
        cls.comic_info.add_section("RSS Feed")
        cls.comic_info.set("RSS Feed", "Build RSS feed", "True")
        cls.comic_info.set("RSS Feed", "Description", "ʀᴜɴ")
        cls.comic_info.set("RSS Feed", "Language", "en")
        cls.comic_info.set("RSS Feed", "image", "rss_banner.png")
        cls.comic_info.set("RSS Feed", "image width", "100")
        cls.comic_info.set("RSS Feed", "image height", "32")

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_build_rss_feed(self, open_mock: MagicMock):
        comic_data = {
            "_title": "I'ma title bay-bee!",
            "_post_date": "January 1, 1903",
            "page_name": "Page 1",
            "comic_paths": ["your_content/comics/Page 1/page_1.png"],
            "_storyline": "Volume 1",
            "_characters": ["Alice", "Bob", "Charlie", "Dennis"],
            "_tags": ["blood", "gore", "sex", "violence"],
            "escaped_alt_text": "Ayo lookit the title on this bitch",
            "post_html": "<p>Why you reading this when there's a perfectly good image up above?</p>",
        }
        build_rss_feed.build_rss_feed(self.comic_info, [comic_data])

        expected = """<?xml version="1.0" ?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
    <channel>
        <atom:link href="https://www.tamberlanecomic.com/feed.xml" rel="self" type="application/rss+xml"/>
        <title>The Dark World of the Furry</title>
        <description>ʀᴜɴ</description>
        <link>https://www.tamberlanecomic.com/</link>
        <dc:creator>Lucifer, Prince of Lies</dc:creator>
        <language>en</language>
        <image>
            <title>The Dark World of the Furry</title>
            <link>https://www.tamberlanecomic.com/</link>
            <url>https://www.tamberlanecomic.com/rss_banner.png</url>
            <width>100</width>
            <height>32</height>
        </image>
        <item>
            <title>I'ma title bay-bee!</title>
            <dc:creator>Lucifer, Prince of Lies</dc:creator>
            <pubDate>Thu, 01 Jan 1903 00:00:00 +0000</pubDate>
            <link>https://www.tamberlanecomic.com/comic/Page 1/</link>
            <guid isPermaLink="true">https://www.tamberlanecomic.com/comic/page_1/</guid>
            <category type="storyline">Volume 1</category>
            <category type="character">Alice</category>
            <category type="character">Bob</category>
            <category type="character">Charlie</category>
            <category type="character">Dennis</category>
            <category type="tag">blood</category>
            <category type="tag">gore</category>
            <category type="tag">sex</category>
            <category type="tag">violence</category>
            <description><![CDATA[<p><img src="https://www.tamberlanecomic.com/your_content/comics/Page 1/page_1.png" alt_text="Ayo lookit the title on this bitch"></p>

<hr>

<p>Why you reading this when there's a perfectly good image up above?</p>]]></description>
        </item>
    </channel>
</rss>
"""
        open_mock().write.assert_called_once_with(expected.encode("utf-8"))

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_build_rss_feed_subdirectory(self, open_mock: MagicMock):
        comic_data = {
            "_title": "I'ma title bay-bee!",
            "_post_date": "January 1, 1903",
            "page_name": "Page 1",
            "comic_paths": ["your_content/comics/Page 1/page_1.png"],
            "_storyline": "Volume 1",
            "_characters": ["Alice", "Bob", "Charlie", "Dennis"],
            "_tags": ["blood", "gore", "sex", "violence"],
            "escaped_alt_text": "Ayo lookit the title on this bitch",
            "post_html": "<p>Why you reading this when there's a perfectly good image up above?</p>",
        }
        comic_info = deepcopy(self.comic_info)
        comic_info.set("Comic Settings", "Comic domain", "JacobWG.github.io")
        comic_info.set("Comic Settings", "Comic subdirectory", "bestcomic")
        build_rss_feed.build_rss_feed(comic_info, [comic_data])

        expected = """<?xml version="1.0" ?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
    <channel>
        <atom:link href="https://JacobWG.github.io/bestcomic/feed.xml" rel="self" type="application/rss+xml"/>
        <title>The Dark World of the Furry</title>
        <description>ʀᴜɴ</description>
        <link>https://JacobWG.github.io/bestcomic/</link>
        <dc:creator>Lucifer, Prince of Lies</dc:creator>
        <language>en</language>
        <image>
            <title>The Dark World of the Furry</title>
            <link>https://JacobWG.github.io/bestcomic/</link>
            <url>https://JacobWG.github.io/bestcomic/rss_banner.png</url>
            <width>100</width>
            <height>32</height>
        </image>
        <item>
            <title>I'ma title bay-bee!</title>
            <dc:creator>Lucifer, Prince of Lies</dc:creator>
            <pubDate>Thu, 01 Jan 1903 00:00:00 +0000</pubDate>
            <link>https://JacobWG.github.io/bestcomic/comic/Page 1/</link>
            <guid isPermaLink="true">https://jacobwg.github.io/bestcomic/comic/page_1/</guid>
            <category type="storyline">Volume 1</category>
            <category type="character">Alice</category>
            <category type="character">Bob</category>
            <category type="character">Charlie</category>
            <category type="character">Dennis</category>
            <category type="tag">blood</category>
            <category type="tag">gore</category>
            <category type="tag">sex</category>
            <category type="tag">violence</category>
            <description><![CDATA[<p><img src="https://JacobWG.github.io/bestcomic/your_content/comics/Page 1/page_1.png" alt_text="Ayo lookit the title on this bitch"></p>

<hr>

<p>Why you reading this when there's a perfectly good image up above?</p>]]></description>
        </item>
    </channel>
</rss>
"""
        open_mock().write.assert_called_once_with(expected.encode("utf-8"))

    def test_add_item(self):
        channel = ElementTree.Element("channel")
        comic_data = {
            "_title": "I'ma title bay-bee!",
            "_post_date": "January 1, 1903",
            "page_name": "Page 1",
            "comic_paths": ["your_content/comics/Page 1/page_1.png"],
            "_storyline": "Volume 1",
            "_characters": ["Alice", "Bob", "Charlie", "Dennis"],
            "_tags": ["blood", "gore", "sex", "violence"],
            "escaped_alt_text": "Ayo lookit the title on this bitch",
            "post_html": "<p>Why you reading this when there's a perfectly good image up above?</p>",
        }
        comic_url = "https://www.tamberlanecomic.com/"

        # Modifies `channel` in-place
        build_rss_feed.add_item(channel, comic_data, comic_url, self.comic_info)

        expected = """<?xml version='1.0' encoding='utf-8'?>
<channel xmlns:dc="http://purl.org/dc/elements/1.1/"><item><title>I'ma title bay-bee!</title><dc:creator>Lucifer, Prince of Lies</dc:creator><pubDate>Thu, 01 Jan 1903 00:00:00 +0000</pubDate><link>https://www.tamberlanecomic.com/comic/Page 1/</link><guid isPermaLink="true">https://www.tamberlanecomic.com/comic/page_1/</guid><category type="storyline">Volume 1</category><category type="character">Alice</category><category type="character">Bob</category><category type="character">Charlie</category><category type="character">Dennis</category><category type="tag">blood</category><category type="tag">gore</category><category type="tag">sex</category><category type="tag">violence</category><description>{post_id_page_1}</description></item></channel>"""
        actual = ElementTree.tostring(channel, xml_declaration=True, encoding='utf-8', method="xml").decode("utf-8")
        self.assertEqual(expected, actual)

        expected = {'post_id_page_1': '''<![CDATA[<p><img src="https://www.tamberlanecomic.com/your_content/comics/Page 1/page_1.png" alt_text="Ayo lookit the title on this bitch"></p>

<hr>

<p>Why you reading this when there\'s a perfectly good image up above?</p>]]>'''}
        actual = build_rss_feed.cdata_dict
        self.assertEqual(expected, actual)

    def test_add_item_multiple(self):
        channel = ElementTree.Element("channel")
        comic_data = {
            "_title": "I'ma title bay-bee!",
            "_post_date": "January 1, 1903",
            "page_name": "Page 1",
            "comic_paths": ["your_content/comics/Page 1/page_1a.png", "your_content/comics/Page 1/page_1b.png"],
            "_storyline": "Volume 1",
            "_characters": ["Alice", "Bob", "Charlie", "Dennis"],
            "_tags": ["blood", "gore", "sex", "violence"],
            "escaped_alt_text": "Ayo lookit the title on this bitch",
            "post_html": "<p>Why you reading this when there's a perfectly good image up above?</p>",
        }
        comic_url = "https://www.tamberlanecomic.com/"
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Info")
        comic_info.set("Comic Info", "Author", "Lucifer, Prince of Lies")
        comic_info.add_section("Comic Settings")
        comic_info.set("Comic Settings", "Date format", "%B %d, %Y")

        # Modifies `channel` in-place
        build_rss_feed.add_item(channel, comic_data, comic_url, self.comic_info)

        expected = """<?xml version='1.0' encoding='utf-8'?>
<channel xmlns:dc="http://purl.org/dc/elements/1.1/"><item><title>I'ma title bay-bee!</title><dc:creator>Lucifer, Prince of Lies</dc:creator><pubDate>Thu, 01 Jan 1903 00:00:00 +0000</pubDate><link>https://www.tamberlanecomic.com/comic/Page 1/</link><guid isPermaLink="true">https://www.tamberlanecomic.com/comic/page_1/</guid><category type="storyline">Volume 1</category><category type="character">Alice</category><category type="character">Bob</category><category type="character">Charlie</category><category type="character">Dennis</category><category type="tag">blood</category><category type="tag">gore</category><category type="tag">sex</category><category type="tag">violence</category><description>{post_id_page_1}</description></item></channel>"""
        actual = ElementTree.tostring(channel, xml_declaration=True, encoding='utf-8', method="xml").decode("utf-8")
        self.assertEqual(expected, actual)

        expected = {'post_id_page_1': '''<![CDATA[<p><img src="https://www.tamberlanecomic.com/your_content/comics/Page 1/page_1a.png" alt_text="Ayo lookit the title on this bitch"></p>
<p><img src="https://www.tamberlanecomic.com/your_content/comics/Page 1/page_1b.png" alt_text="Ayo lookit the title on this bitch"></p>

<hr>

<p>Why you reading this when there\'s a perfectly good image up above?</p>]]>'''}
        actual = build_rss_feed.cdata_dict
        self.assertEqual(expected, actual)
