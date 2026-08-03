import hashlib
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
RESUME_FILENAME = "Alex_Bogle_IT_Support_Resume.pdf"
RESUME = ROOT / RESUME_FILENAME
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
        self.assertEqual(self.html.count(resume_link), 2)
        safe_resume_link = (
            f'href="{RESUME_FILENAME}" target="_blank" '
            'rel="noopener noreferrer"'
        )
        self.assertEqual(self.html.count(safe_resume_link), 2)
        self.assertEqual(self.html.count("Download Resume"), 2)

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
        self.assertIn("Evidence first", self.html)
        self.assertIn("Lab", self.html)
        self.assertIn("Work in progress", self.html)
        self.assertIn("What this proves", self.html)
        self.assertIn("What this does not prove", self.html)

    def test_high_risk_claims_are_absent(self):
        forbidden = (
            "production-grade",
            "production metrics",
            "tests passing",
            "all passing",
            "every system below is deployed",
            "agentic systems architect",
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

    def test_unverified_work_history_is_not_published(self):
        for phrase in (
            "Sterling Carter",
            "Island Networks",
            "Security Options",
            "Reliable Courier",
            "6,000+ assets",
            "57% improvement",
            "35% faster",
        ):
            self.assertNotIn(phrase.lower(), self.lower)

    def test_compromised_repository_is_not_promoted(self):
        self.assertNotIn('href="https://github.com/SaintChris/rag-eval-system"', self.html)
        self.assertIn("Repository link withheld pending credential rotation", self.html)

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
        self.assertLess(INDEX.stat().st_size, 40_000)

    def test_accessible_structure(self):
        tags = [tag for tag, _ in self.parser.tags]
        self.assertIn("header", tags)
        self.assertIn("nav", tags)
        self.assertIn("main", tags)
        self.assertIn("footer", tags)
        self.assertIn("h1", tags)
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

    def test_no_inline_styles_or_implicit_buttons(self):
        self.assertIsNone(re.search(r"\sstyle=", self.html, re.IGNORECASE))
        for tag, attrs in self.parser.tags:
            if tag == "button":
                self.assertIn("type", attrs)


if __name__ == "__main__":
    unittest.main()
