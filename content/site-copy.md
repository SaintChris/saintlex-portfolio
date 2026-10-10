# Site copy: saintlex.sbs redesign (October 2026)

Public copy for the HTML build. Case-study bodies are in `case-studies/`.

## Hero

Eyebrow: Based in Jamaica

Title: IoT & AI Technician

Lead: I build and run AI and automation tools for IREE Solar, a solar and battery installer in Jamaica. That includes a staff assistant that answers from product documents, a website chat that only cites approved facts, and performance reports built from monitoring data.

Links: Email me · LinkedIn · GitHub

## Now

Now: running the staff assistant pilot and getting the redesigned company website ready for launch.

## Selected work

Card order and one-line summaries. Status labels are fixed.

1. IREE Staff Assistant and Website Chat · Production pilot
   A staff assistant over 32 product documents and a public website chat, with rate limits, prompt-injection guards and a question set I rerun after every change.
2. IREE Solar Website Redesign · Professional work — launch pending
   A 15-page Squarespace redesign built from Git source, checked at seven screen widths, and verified against the saved site after every save.
3. Solar and Battery Performance Reporting · Professional work
   Customer and internal PDF reports from Tesla Powerhub data, with a read-only collector and strict rules about what the data can and can't show.
4. AI-Assisted Engineering Workstation · Personal tooling
   My setup for working with AI coding agents: local memory, a task API, nightly upkeep and guard rails on risky commands.
5. Android Linux Homelab · Sanitized case study
   An old phone turned into a constrained Linux web server.

## Experience

### IREE Solar · IoT & AI Technician · Current role (since August 2026)

I work across IoT, AI-assisted automation, systems integration, networking and technical documentation for a solar and battery installer.

- Built and run a staff AI assistant that answers from 32 manufacturer documents, with access control, per-person rate limits and a fixed evaluation set.
- Built a website chat for customer questions that answers only from reviewed public facts, cites its source, and refers anything else to the team.
- Redesigned the company website on Squarespace from version-controlled source. Launch is pending approval.
- Produce customer and internal performance reports for solar and battery sites from Tesla Powerhub data.
- Run the server behind these tools: Docker, gated staff access, CI image builds and scans, health checks, and nightly backups with a tested restore.

### Earlier roles

- Sterling Carter Technology Distributors · IT Procurement Administrator · Temporary contract. Configured and upgraded desktop computers, tested printers and kept technical order records.
- Island Networks Jamaica · Asset and Inventory Management Officer, Level II · Temporary contract. Administered technical asset records and supported device provisioning, firmware and configuration work.
- IBEX, Fitbit Account · Technical Support Specialist. Troubleshot device setup, Bluetooth pairing, sync, firmware and app connectivity.
- Reliable Courier Jamaica · Customer Service Representative with internal technology support responsibilities. Set up laptops, printers, phones, software, and user accounts, and fixed everyday access and connectivity problems.

## Stack

### Daily

Linux (Ubuntu), Bash, Docker and Compose, Git and GitHub, GitHub Actions, Python, Node.js, JavaScript, TypeScript, REST and GraphQL APIs, Open WebUI, document retrieval (hybrid search, reranking, ChromaDB), hosted LLM APIs, Cloudflare Access and Tunnel, Caddy, Squarespace, Tailwind CSS, n8n, AI coding agents.

### Energy systems

Tesla Powerhub, Tesla Powerwall systems, ServiceM8, solar PV and battery monitoring, grid outage and battery reserve analysis, manufacturer datasheets for inverters, batteries and panels.

### Foundation

Earlier support and operations work: Salesforce, Autotask, AssetTiger, Google Workspace, Slack, PuTTY, QuickBooks Enterprise, River Cities, ASYCUDA World, hardware setup and upgrades, device and firmware troubleshooting, networking diagnostics, AWS fundamentals.

## How I work

1. Read before changing. Find out what the system does now and what still has to work after the change.
2. Collect evidence. Logs, data and the actual error, not guesses. A reporting gap isn't an equipment fault.
3. Make small changes I can undo. Take a restore point first. Keep secrets and customer data out of code, notes and logs.
4. Check it the way a user would. Read the result back, run the tests, open it on the device.
5. Write it down. What changed, why, and what's still open.

I use AI coding agents for a lot of my implementation work. I set the scope, review what they produce, and check the result myself before it ships.

## Footer

Alex Bogle · Jamaica
IoT & AI Technician · Updated October 2026

## Notes for the HTML build

The existing tests in `tests/test_portfolio.py` check some exact strings in `index.html`. This copy keeps them, with two exceptions to resolve:

- The footer says "Updated October 2026". The test still expects "Updated September 2026" and needs updating.
- The test forbids the words "react", "vue", "angular", "svelte" and "next.js", and phrases such as "ai engineer" and "software engineer", anywhere in `index.html`. This copy avoids them. That's why the workstation card is titled "AI-Assisted Engineering Workstation". Keep the case-study text off `index.html` or re-check it against that list.
- Strings this copy already supplies for the tests: "Based in Jamaica", "IoT & AI", "AI-assisted automation", "temporary contract", the four earlier-role opening phrases, every Foundation tool name, Linux and Bash.
- Strings the tests need that this copy doesn't cover (keep them from the current page): the "Professional Direction" section and its six roles, the section headings ("Technical Focus", "Engineering Method", "Professional Experience", "Technical Projects", "Tools and Platforms", "Contact"), and the RAG Evaluation Lab and IoT Energy Telemetry Lab labels ("Local experiment", "Current limitation", the withheld-repository sentence).
- The hero no longer says "Open to eligible remote opportunities". No test requires it.
