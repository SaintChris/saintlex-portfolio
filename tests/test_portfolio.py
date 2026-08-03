import hashlib
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
RESUME_FILENAME = "Alex_Bogle_IT_Support_Resume.pdf"
RESUME = ROOT / RESUME_FILENAME
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
MANIFEST = ROOT / "manifest.json"
SOCIAL_PREVIEW = ROOT / "social-preview.png"
RESUME_SHA256 = "103b8630fcc500142bbb1586d0acfad86a512907f085cb3194859427219e2b34"
RECRUITER_EMAIL = "bogle.alex@hotmail.com"


class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.tags = []
        self.title_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

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
        self.assertEqual(title, "Alex Bogle | IT Support & Technical Operations")
        self.assertIn("IT Support &amp; Technical Operations", self.html)
        self.assertIn("Based in Jamaica", self.html)

    def test_target_roles_are_explicit(self):
        for role in (
            "IT Support",
            "IT Help Desk",
            "Technical Support",
            "Application Support",
            "IT Operations Support",
            "Cloud Support Trainee",
            "Implementation Support",
        ):
            self.assertIn(role, self.html)

    def test_verified_resume_file_is_published(self):
        self.assertTrue(RESUME.is_file())
        resume_bytes = RESUME.read_bytes()
        self.assertTrue(resume_bytes.startswith(b"%PDF-"))
        self.assertEqual(hashlib.sha256(resume_bytes).hexdigest(), RESUME_SHA256)

    def test_recruiter_email_is_public_in_contact_section(self):
        contact = re.search(
            r'<section class="contact".*?</section>', self.html, re.DOTALL
        )
        self.assertIsNotNone(contact)
        contact_html = contact.group(0) if contact else ""
        self.assertIn(f'href="mailto:{RECRUITER_EMAIL}"', contact_html)
        self.assertIn(f">{RECRUITER_EMAIL}<", contact_html)

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
        self.assertEqual(
            locations,
            {
                "https://saintlex.sbs/",
                f"https://saintlex.sbs/{RESUME_FILENAME}",
            },
        )

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
        self.assertIn("Updated August 2026", self.html)
        self.assertNotIn("Updated July 2026", self.html)

    def test_hero_and_contact_link_to_verified_resume(self):
        resume_link = f'href="{RESUME_FILENAME}"'
        hero = re.search(
            r'<section class="hero".*?</section>', self.html, re.DOTALL
        )
        contact = re.search(
            r'<section class="contact".*?</section>', self.html, re.DOTALL
        )
        self.assertIsNotNone(hero)
        self.assertIsNotNone(contact)
        hero_html = hero.group(0) if hero else ""
        contact_html = contact.group(0) if contact else ""
        self.assertIn(resume_link, hero_html)
        self.assertIn(resume_link, contact_html)
        self.assertEqual(self.html.count(resume_link), 3)
        safe_resume_link = (
            f'href="{RESUME_FILENAME}" target="_blank" '
            'rel="noopener noreferrer"'
        )
        self.assertEqual(self.html.count(safe_resume_link), 3)
        self.assertEqual(self.html.count(">Download Resume <"), 2)

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

    def test_honest_scope_and_evidence_labels(self):
        self.assertIn("Work in progress", self.html)
        self.assertIn("Local experiment", self.html)
        self.assertIn("Current limitation", self.html)
        self.assertNotIn("What this proves", self.html)
        self.assertNotIn("What this does not prove", self.html)

    def test_direct_recruiter_copy_and_verified_toolkit(self):
        direct_headings = (
            "Support Skills",
            "Troubleshooting Process",
            "Professional Support Experience",
            "Technical Projects",
            "Tools and Platforms",
            "Target Roles",
            "Contact",
        )
        for heading in direct_headings:
            self.assertIn(heading, self.html)

        formulaic_copy = (
            "Practical support, not a keyword wall.",
            "A repeatable path from symptom to resolution.",
            "Labs and documentation with honest boundaries.",
            "Depth matters more than a long list.",
            "Where I can contribute and keep growing.",
            "Evidence first",
            "Claims linked to work",
        )
        for phrase in formulaic_copy:
            self.assertNotIn(phrase, self.html)

        for tool in (
            "Salesforce",
            "Autotask",
            "AssetTiger",
            "Google Workspace",
            "Slack",
            "PuTTY",
            "QuickBooks Enterprise",
            "River Cities",
            "ASYCUDA World",
            "Linux",
            "Networking diagnostics",
            "Bash",
            "AWS fundamentals",
        ):
            self.assertIn(tool, self.html)
        self.assertNotIn("Local AI tools", self.html)

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

    def test_verified_professional_experience_is_published(self):
        verified_experience = {
            "Sterling Carter Technology Distributors": (
                "IT Procurement Administrator",
                "Configured and upgraded desktop computers",
            ),
            "Island Networks Jamaica": (
                "Asset and Inventory Management Officer",
                "Administered technical asset records",
            ),
            "IBEX, Fitbit Account": (
                "Technical Support Specialist",
                "Troubleshot device setup",
            ),
            "Reliable Courier Jamaica": (
                "Customer Service Representative",
                "Set up laptops, printers, phones, software, and user accounts",
            ),
        }
        for employer, expected_text in verified_experience.items():
            self.assertIn(employer, self.html)
            for text in expected_text:
                self.assertIn(text, self.html)
        self.assertIn("temporary contract", self.lower)
        self.assertLess(self.html.index('id="experience"'), self.html.index('id="evidence"'))

    def test_compromised_repository_is_not_promoted(self):
        self.assertNotIn('href="https://github.com/SaintChris/rag-eval-system"', self.html)
        self.assertIn("repository link remains withheld while credential rotation", self.lower)

    def test_stale_resume_and_commercial_pages_are_removed(self):
        self.assertNotIn("Alex_Bogle_Resume_2026.pdf", self.html)
        self.assertFalse((ROOT / "Alex_Bogle_Resume_2026.pdf").exists())
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

    def test_accessible_structure(self):
        tags = [tag for tag, _ in self.parser.tags]
        self.assertIn("header", tags)
        self.assertIn("nav", tags)
        self.assertIn("main", tags)
        self.assertIn("footer", tags)
        self.assertIn("h1", tags)
        self.assertTrue(
            any(
                tag == "main"
                and attrs.get("id") == "main-content"
                and attrs.get("tabindex") == "-1"
                for tag, attrs in self.parser.tags
            )
        )
        self.assertTrue(
            any(tag == "ol" and attrs.get("class") == "steps" for tag, attrs in self.parser.tags)
        )
        self.assertTrue(
            any(tag == "ul" and attrs.get("class") == "role-list" for tag, attrs in self.parser.tags)
        )
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)))
        internal_targets = {value for value in self.parser.ids}
        for href in self.parser.hrefs:
            if href.startswith("#") and href != "#":
                self.assertIn(href[1:], internal_targets)

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


if __name__ == "__main__":
    unittest.main()
