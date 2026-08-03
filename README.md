# Alex Bogle Portfolio

[![Live site](https://img.shields.io/badge/live-saintlex.sbs-0f62fe)](https://saintlex.sbs/)
[![CI](https://github.com/SaintChris/saintlex-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/SaintChris/saintlex-portfolio/actions/workflows/ci.yml)

Recruiter-focused portfolio for Alex Bogle, an IT support and technical operations professional based in Jamaica. The homepage presents verified customer support, device troubleshooting, hardware setup, asset management, documentation, and operational experience alongside clearly labeled technical projects.

## Positioning

The site targets:

- IT Help Desk
- Technical Support
- Application Support
- IT Operations Support
- Cloud Support Trainee
- Implementation Support

The site uses only already-confirmed facts. Download the verified IT Support resume for details about employment history, technical support experience, and operational background.

## Content policy

- Labs are labeled as labs.
- Work in progress is labeled clearly.
- Professional experience comes from the verified resume.
- Project status and current limitations are stated where relevant.
- No performance, uptime, customer-result, or deployment claim is published without current evidence.
- Stale operational telemetry is not displayed publicly.

## Technology

- Semantic HTML
- Handwritten responsive CSS
- No client-side framework
- No public API keys or telemetry
- GitHub Pages with a custom domain
- Python content tests and `html-validate` in CI
- Canonical, Open Graph, Twitter card, JSON-LD, sitemap, and robots metadata

## Local verification

```bash
python3 -m unittest tests/test_portfolio.py -v
npx html-validate index.html
```

## Public links

- Site: https://saintlex.sbs/
- Resume: https://saintlex.sbs/Alex_Bogle_IT_Support_Resume.pdf
- Recruiter email: bogle.alex@hotmail.com
- GitHub: https://github.com/SaintChris
- LinkedIn: https://www.linkedin.com/in/alex-bogle/
