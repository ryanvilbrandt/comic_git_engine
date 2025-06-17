from configparser import RawConfigParser
from unittest import TestCase
from xml.etree import ElementTree

from scripts import build_rss_feed


class TestRssFeed(TestCase):

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
        comic_url = "https://www.tamberlanecomic.com"
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Info")
        comic_info.set("Comic Info", "Author", "Lucifer, Prince of Lies")
        comic_info.add_section("Comic Settings")
        comic_info.set("Comic Settings", "Date format", "%B %d, %Y")

        # Modifies `channel` in-place
        build_rss_feed.add_item(channel, comic_data, comic_url, comic_info)

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
        comic_url = "https://www.tamberlanecomic.com"
        comic_info = RawConfigParser()
        comic_info.add_section("Comic Info")
        comic_info.set("Comic Info", "Author", "Lucifer, Prince of Lies")
        comic_info.add_section("Comic Settings")
        comic_info.set("Comic Settings", "Date format", "%B %d, %Y")

        # Modifies `channel` in-place
        build_rss_feed.add_item(channel, comic_data, comic_url, comic_info)

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
