import json
import re
import struct
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
MANIFEST = ROOT / "manifest.json"
SOCIAL_PREVIEW = ROOT / "social-preview.png"
RECRUITER_EMAIL = "bogle.alex@hotmail.com"


class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.tags = []
        self.title_parts = []
        self._in_title = False
        self._svg_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "svg":
            self._svg_depth += 1
        # Only the document <title> counts; SVG <title> elements are labels.
        if tag == "title" and self._svg_depth == 0:
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "svg" and self._svg_depth:
            self._svg_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)


class PortfolioContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.lower = cls.html.lower()
        cls.parser = PortfolioParser()
        cls.parser.feed(cls.html)

    def test_recruiter_facing_title_and_headline(self):
        title = "".join(self.parser.title_parts).strip()
        self.assertEqual(title, "Alex Bogle | IoT & AI Technician")
        self.assertIn("IoT &amp; AI", self.html)
        self.assertIn("IREE Solar in Jamaica", self.html)

    def test_resume_file_is_not_published(self):
        self.assertFalse((ROOT / "Alex_Bogle_IT_Support_Resume.pdf").exists())
        self.assertNotIn("Alex_Bogle_IT_Support_Resume.pdf", self.html)
        self.assertNotIn("Download Resume", self.html)


    def test_public_profile_links_remain_available(self):
        self.assertIn('href="https://www.linkedin.com/in/alex-bogle/"', self.html)
        self.assertIn('href="https://github.com/SaintChris"', self.html)

    def test_canonical_social_and_structured_metadata(self):
        self.assertIn('<link rel="canonical" href="https://saintlex.sbs/">', self.html)
        for property_name in ("og:type", "og:title", "og:description", "og:url", "og:image"):
            self.assertRegex(
                self.html,
                rf'<meta property="{re.escape(property_name)}" content="[^"]+">',
            )
        for name in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
            self.assertRegex(
                self.html,
                rf'<meta name="{re.escape(name)}" content="[^"]+">',
            )
        self.assertIn("https://saintlex.sbs/social-preview.png", self.html)

        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1) if match else "{}")
        self.assertEqual(data["@type"], "ProfilePage")
        self.assertEqual(data["url"], "https://saintlex.sbs/")
        self.assertEqual(data["mainEntity"]["name"], "Alex Bogle")
        self.assertEqual(data["mainEntity"]["email"], f"mailto:{RECRUITER_EMAIL}")
        self.assertIn("https://www.linkedin.com/in/alex-bogle/", data["mainEntity"]["sameAs"])
        self.assertIn("https://github.com/SaintChris", data["mainEntity"]["sameAs"])

    def test_indexing_manifest_and_preview_assets(self):
        self.assertTrue(ROBOTS.is_file())
        robots = ROBOTS.read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://saintlex.sbs/sitemap.xml", robots)

        self.assertTrue(SITEMAP.is_file())
        sitemap_root = ET.parse(SITEMAP).getroot()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in sitemap_root.findall("sm:url/sm:loc", namespace)}
        self.assertEqual(locations, {"https://saintlex.sbs/"})

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("professional", manifest["description"].lower())
        self.assertTrue(manifest.get("icons"))
        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', self.html)
        self.assertTrue((ROOT / "favicon.svg").is_file())

        self.assertTrue(SOCIAL_PREVIEW.is_file())
        header = SOCIAL_PREVIEW.read_bytes()[:24]
        self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", header[16:24]), (1200, 630))

    def test_footer_date_is_current(self):
        self.assertIn("Updated October 2026", self.html)
        self.assertNotIn("Updated September 2026", self.html)
        self.assertNotIn("Updated July 2026", self.html)

    def test_outdated_resume_notices_are_absent(self):
        source_suffixes = {".css", ".html", ".json", ".md", ".yaml", ".yml"}
        source_text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and path.suffix in source_suffixes
        )
        outdated = (
            "employment history and role-specific " + "résumé are being reconciled",
            "employment history and role specific " + "resume are still being reconciled",
            "resume download will return after the verified it support version is complete",
            "résumé download will return after the verified it-support version is complete",
            "employment history is intentionally " + "withheld",
            "downloadable résumé are intentionally " + "withheld",
        )
        for phrase in outdated:
            self.assertNotIn(phrase, source_text)

    def test_high_risk_claims_are_absent(self):
        forbidden = (
            "production-grade",
            "production metrics",
            "tests passing",
            "all passing",
            "every system below is deployed",
            "agentic systems architect",
            "ai engineer",
            "devops engineer",
            "senior cloud engineer",
            "software engineer",
            "production systems architect",
            "zero monthly inference costs",
            "$0/month",
            "$0/mo",
            "live openrouter",
            "openrouter dashboard",
            "22k+",
            "24/7 local",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, self.lower)

    def test_stale_resume_and_commercial_pages_are_removed(self):
        self.assertNotIn("Alex_Bogle_Resume_2026.pdf", self.html)
        self.assertFalse((ROOT / "Alex_Bogle_Resume_2026.pdf").exists())
        self.assertFalse((ROOT / "Alex_Bogle_IT_Support_Resume.pdf").exists())
        self.assertFalse((ROOT / "proposal.html").exists())
        self.assertFalse((ROOT / "pricing.html").exists())
        self.assertFalse((ROOT / ".github/workflows/update-or-stats.yml").exists())
        self.assertFalse((ROOT / "data/telemetry.json").exists())

    def test_page_is_static_and_self_contained(self):
        self.assertTrue(CSS.exists())
        self.assertNotIn("cdn.tailwindcss.com", self.html)
        self.assertNotIn("OPENROUTER", self.html)
        self.assertIsNone(re.search(r'<script[^>]+src=', self.html, re.IGNORECASE))
        for framework in ("react", "vue", "angular", "svelte", "next.js"):
            self.assertNotIn(framework, self.lower)
        self.assertLess(INDEX.stat().st_size, 40_000)

    def test_external_links_are_safe(self):
        for tag, attrs in self.parser.tags:
            if tag == "a" and attrs.get("target") == "_blank":
                rel = set(attrs.get("rel", "").split())
                self.assertTrue({"noopener", "noreferrer"}.issubset(rel))
                self.assertIn("opens", attrs.get("aria-label", "").lower())

    def test_no_inline_styles_or_implicit_buttons(self):
        self.assertIsNone(re.search(r"\sstyle=", self.html, re.IGNORECASE))
        for tag, attrs in self.parser.tags:
            if tag == "button":
                self.assertIn("type", attrs)

    def test_one_screen_content(self):
        self.assertEqual(self.html.count('<li>'), 3)
        for project in ("Staff assistant", "Website and customer chat", "Solar performance reports"):
            self.assertIn(f"<strong>{project}</strong>", self.html)
        for removed in ("Selected work", "Experience", "How I work", "<nav", "<details"):
            self.assertNotIn(removed, self.html)

    def test_public_contact_channels(self):
        self.assertIn(f'href="mailto:{RECRUITER_EMAIL}"', self.html)
        self.assertRegex(self.html, rf">{re.escape(RECRUITER_EMAIL)}<")
        self.assertNotIn(".pdf", self.lower)

    def test_no_private_operational_details(self):
        for term in ("saintlex.tech", "iree-vps", "vultr", "grok", "kemmar", "millsborough",
                     "levy", "ste20", "powerhub", "open webui", "cloudflare"):
            self.assertNotIn(term, self.lower)

    def test_sun_path_is_accessible(self):
        self.assertRegex(self.html, r'<svg[^>]+role="img"[^>]+aria-labelledby="sun-title"')
        self.assertIn('<title id="sun-title">', self.html)
        self.assertIn("America/Jamaica", self.html)

    def test_accessible_structure(self):
        tags = [tag for tag, _ in self.parser.tags]
        self.assertIn("main", tags)
        self.assertIn("footer", tags)
        self.assertEqual(tags.count("h1"), 1)
        self.assertTrue(any(tag == "main" and attrs.get("id") == "main-content"
                            for tag, attrs in self.parser.tags))
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)))


if __name__ == "__main__":
    unittest.main()
