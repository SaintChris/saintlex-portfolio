# AI Agent Infrastructure Showcase

> **Production AI agent framework with multi-agent orchestration, automated knowledge management, and 24/7 autonomous workflows.**
> Built on the Hermes agent framework with Paperclip orchestration.

## What This Is

A full production AI agent infrastructure setup — not a tutorial, not a toy. This is a live system running 26 autonomous cron jobs handling financial tracking, market analysis, content pipelines, and system operations around the clock.

## Key Components

- **6 Specialized Agent Inboxes** — CEO, Market Analyst, Content Growth, Finance, Ops, Research
- **Paperclip Orchestration** — Multi-agent task delegation and issue tracking
- **Obsidian Knowledge Management** — Structured knowledge base with automated updates
- **26 Cron Jobs** — Autonomous workflows running 24/7
- **PostgreSQL Backend** — Persistent storage with pgvector for semantic search

## Architecture

```
                   ┌─────────────────────┐
                   │   Hermes Framework   │
                   │   (Agent Runtime)    │
                   └──────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │  Paperclip  │    │  Obsidian   │    │  PostgreSQL │
   │  (orchestr.)│    │  (knowledge)│    │  (storage)  │
   └─────────────┘    └─────────────┘    └─────────────┘
          │
          ▼
   ┌─────────────────────────────────────┐
   │         26 Cron Jobs                │
   │  P&L · Market · Content · Ops · ... │
   └─────────────────────────────────────┘
```

## What It Automates

| Workflow | Frequency | Agent |
|----------|-----------|-------|
| P&L Tracking | Weekly | Finance |
| Market Analysis | Daily | Market Analyst |
| Content Pipeline | Daily | Content Growth |
| System Health | Hourly | Ops |
| Research Digest | Daily | Research |
| Session Archiving | Per-session | Ops |

## Tech Stack

- **Hermes Framework** — Multi-agent runtime with delegation patterns
- **Paperclip** — Issue tracking and orchestration
- **Obsidian API** — Knowledge base management
- **PostgreSQL + pgvector** — Persistent storage with vector search
- **Python 3.11+** — Core automation scripts

## Repository Contents

```
hermes-setup-showcase/
├── index.html          # Landing page / service showcase
├── docs/               # Setup guides and architecture docs
└── README.md           (this file)
```

## Why This Matters

This isn't just code — it's a **live production system** that:

1. **Runs autonomously** — 26 scheduled workflows with zero manual intervention
2. **Manages knowledge** — Automated Obsidian vault updates from agent outputs
3. **Tracks finances** — Automated P&L reporting and budget monitoring
4. **Orchestrates agents** — Real multi-agent coordination, not sequential scripts

## Live Demo

See it in action: [saintlex.sbs](https://saintlex.sbs)

---

**Author:** [Alex Bogle](https://saintlex.sbs) · [LinkedIn](https://linkedin.com/in/alex-bogle) · [GitHub](https://github.com/SaintChris)