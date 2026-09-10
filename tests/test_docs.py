"""Migration checks against the old engine's URLs and the built site."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from scripts.docs import ROOT, excerpt, read_posts, rewrite_links


class BlogMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.posts = read_posts()
        cls.preview = read_posts(preview=True)
        cls.site = ROOT / "site"

    def soup(self, path):
        return BeautifulSoup((self.site / path).read_text(), "html.parser")

    def test_existing_urls_are_preserved(self):
        # Captured from Material's blog plugin before migration, including drafts.
        baseline = json.loads((ROOT / "tests/post-urls.json").read_text())
        current = {p["source"]: p["url"] for p in self.preview}
        for source, url in baseline.items():
            if source in current:
                self.assertEqual(url, current[source], source)

    def test_published_posts_have_canonical_urls_and_comments(self):
        for post in self.posts:
            soup = self.soup(post["url"] + "index.html")
            self.assertEqual("https://netdevops.me/" + post["url"], soup.select_one('link[rel="canonical"]')["href"])
            self.assertIsNotNone(soup.select_one("article h1"))
            if post["meta"].get("comments"):
                self.assertIsNotNone(soup.select_one("script[data-repo='hellt/netdevops.me']"))

    def test_drafts_only_appear_in_preview(self):
        drafts = [p for p in self.preview if p["draft"]]
        self.assertTrue(drafts)
        search = (self.site / "search.json").read_text()
        for post in drafts:
            self.assertFalse((self.site / post["url"] / "index.html").exists())
            self.assertNotIn(post["url"], search)

    def test_all_posts_are_discoverable_in_pagination(self):
        pages = [self.site / "index.html", *self.site.glob("page/*/index.html")]
        links = {a["href"] for path in pages for a in BeautifulSoup(path.read_text(), "html.parser").select("article a[href]")}
        for post in self.posts:
            self.assertIn("/" + post["url"], links)
        self.assertTrue((self.site / "page/2/index.html").exists())

    def test_sitemap_includes_unlisted_posts_and_pages(self):
        urls = {n.text for n in ET.parse(self.site / "sitemap.xml").iter() if n.tag.endswith("}loc")}
        for post in self.posts:
            self.assertIn("https://netdevops.me/" + post["url"], urls)
        self.assertIn("https://netdevops.me/page/2/", urls)
        self.assertIn("https://netdevops.me/about/", urls)

    def test_feeds_keep_permalinks_and_exclude_drafts(self):
        allowed = {"https://netdevops.me/" + p["url"] for p in self.posts}
        for kind in ("created", "updated"):
            items = ET.parse(self.site / f"feed_rss_{kind}.xml").findall("./channel/item")
            self.assertEqual(min(20, len(self.posts)), len(items))
            for item in items:
                url = item.findtext("link")
                self.assertIn(url, allowed)
                self.assertEqual(url, item.findtext("guid"))
                self.assertEqual(url + "#__comments", item.findtext("comments"))
                self.assertLessEqual(len(item.findtext("description")), 5000)

    def test_macros_lightboxes_and_search(self):
        post = next(p for p in self.posts if p["source"].endswith("gnmic-openconfig.md"))
        soup = self.soup(post["url"] + "index.html")
        self.assertEqual(3, len(soup.select(".ext-code-divider")))
        self.assertTrue(soup.select("a.glightbox"))
        self.assertNotIn("[[[ header_divider ]]]", str(soup))
        search = json.loads((self.site / "search.json").read_text())
        self.assertTrue(search)
        self.assertIn("gNMI", json.dumps(search))

    def test_native_tag_listing(self):
        soup = self.soup("tags/index.html")
        self.assertNotIn("[TAGS]", soup.get_text())
        links = {unquote(urlsplit(a["href"]).path) for a in soup.select("article a[href]")}
        self.assertTrue(any("using-orbstack" in path for path in links))

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed to execute the browser search worker")
    def test_browser_search_worker_returns_posts(self):
        config = json.loads(self.soup("index.html").select_one("script#__config").string)
        worker = self.site / config["search"].removeprefix("./").lstrip("/")
        subprocess.run(
            ["node", str(ROOT / "tests/search-worker.cjs"), str(self.site / "search.json"), str(worker)],
            check=True, capture_output=True, text=True, timeout=30,
        )

    def test_custom_domain_and_404(self):
        self.assertEqual("netdevops.me", (self.site / "CNAME").read_text().strip())
        self.assertTrue((self.site / ".nojekyll").exists())
        self.assertIsNotNone(self.soup("404.html").select_one("h1#__skip"))

    def test_link_rewriting_preserves_anchors_and_code(self):
        body = '[post](../2020/gnmic.md#intro)\n```md\n[post](../2020/gnmic.md#intro)\n```\n'
        result = rewrite_links(body, "posts/2022/test.md", {"posts/2020/gnmic.md": "2020/gnmic/"})
        self.assertTrue(result.startswith("[post](/2020/gnmic/#intro)"))
        self.assertIn("```md\n[post](../2020/gnmic.md#intro)", result)

    def test_excerpt_keeps_late_reference_definitions_isolated(self):
        first = excerpt({"body": "# First\n\n[Example][site]\n<!-- more -->\n[site]: https://example.org\n"}, 1)
        second = excerpt({"body": "# Second\n\n[Example][site]\n<!-- more -->\n[site]: https://example.net\n"}, 2)
        import markdown
        soup = BeautifulSoup(markdown.markdown(first + "\n" + second), "html.parser")
        self.assertEqual(["https://example.org", "https://example.net"], [a["href"] for a in soup.select("a")])


if __name__ == "__main__":
    unittest.main()
