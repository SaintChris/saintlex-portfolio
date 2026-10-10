# Sanitization check: content pack, October 2026

Files covered: `case-studies/iree-staff-assistant.md`, `case-studies/iree-website-redesign.md`, `case-studies/solar-performance-reporting.md`, `case-studies/ai-engineering-workstation.md`, `content/site-copy.md`. `case-studies/android-linux-homelab.md` is unchanged.

Checked by reading each file and by a case-insensitive search for hostnames, IP addresses, email addresses, provider and vendor names, staff and customer names, site IDs, money amounts, and the words contract, salary, probation, cost and subscription.

## Rules

| Rule | Result |
| --- | --- |
| No customer or site names, addresses, or STE/site IDs | Complies. Reports say "a few customer sites" only. |
| No staff names (including managers and coworkers) | Complies. The website study says "the manager's notes" without a name. |
| No salary, contract, probation or blocker-register content | Complies. "Temporary contract" appears only for the two earlier roles, as on the current site and as the tests require. |
| No costs, vendor plans or subscriptions | Complies. Rate limits are described as mechanisms, with no amounts. |
| No hostnames, subdomains, server names, IPs or server provider names | Complies. The diagram uses generic component names. Cloudflare is named as a tool (Access, Tunnel) in two stack lists, not as a hostname. |
| No account emails | Complies. |
| No private repository names | Complies. No repository names or links appear. |
| No internal decisions, rebrand or domain plans | Complies. The website study mentions redirects from old pages only, not any domain change. |
| LLM vendor not named for IREE systems | Complies. IREE copy says "hosted LLM" and "fallback model". The workstation study names Claude Code and Codex as Alex's own personal tools (see sign-off list). |
| No invented metrics | Complies. Every number comes from the vault notes, repo READMEs or skill: 32 documents, 51 eval questions, 15 and 20 pages, seven screen widths, three forms, five-minute health check, 15-minute and one-minute data. No scores, percentages, costs or user counts are given. |
| Redesigned IREE website not linked, launch pending | Complies. No link. Status is "Professional work — launch pending" and the text says it's password-protected and waiting on launch approval. |
| No job-hunting language | Complies. "Open to eligible remote opportunities" is dropped from the hero. No "candidate" or "opportunities" wording. |
| Nothing read from the vault's Private folder | Complies. |

## Claims needing Alex's or the employer's sign-off

1. Naming IREE Solar with this level of detail on a public site: staff assistant, website chat, website redesign, performance reports.
2. "Production pilot" for the staff assistant, and the statement that it runs as a pilot on the company server.
3. Describing the website chat's safety design publicly: approved-source citations, injection and output guards, no transcripts or IP addresses kept, per-visitor and daily limits, fallback model.
4. Describing the access setup: an access gateway with a path allowlist, Cloudflare Access and Tunnel in the stack, nightly encrypted backups to an on-site machine, restore drill.
5. The figures "32 product documents" and "51 questions at last count" for the evaluation set, and the embedding-model revert story.
6. Mentioning the redesign before launch at all, including "15 pages", "20 pages", the Git-built Squarespace code and the two bugs found in review (FAQ filter, chat retry limit).
7. Naming Tesla Powerhub and describing the report method: a read-only script in Alex's signed-in portal session while API access is pending. Tesla's portal terms may matter here as well as the employer's view.
8. "Has been used for a few customer sites", and the description of what the customer and internal reports contain.
9. The operations dashboard prototype: simulated data only, no customer equipment connected.
10. Saying that AI coding agents did much of the implementation on the website and the assistant. This is accurate, but it's Alex's call how to frame it.
11. Naming Claude Code and Codex in the workstation study, and describing Alex's personal setup (Obsidian vault, local memory service, patched Super Productivity build, command guard and its unresolved background-session issue).
12. "Since August 2026" as the IREE start date.
13. n8n, Open WebUI and ServiceM8 listed in the stack as tools Alex uses for IREE work.

## Notes for the HTML build

See the end of `content/site-copy.md`. In short, the footer date conflicts with the current test ("Updated September 2026"), and `index.html` must not contain the framework words or job titles the tests forbid.
