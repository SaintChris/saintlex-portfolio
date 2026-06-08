---
title: Hermes Agent – Zero‑Cost, Multi‑Layer AI Operations Blueprint
date: 2026-06-08
tags: [hermes, agent, zero-cost, architecture, automation, honcho, kanban]
---

## TL;DR
Hermes Agent runs on a **single M1 Mac** with **no monthly cloud spend** by combining:

| Layer | What it does | Key tech |
|------|--------------|----------|
| **Core inference** | Local Ollama model (`qwen3:4b`) with OpenRouter fall‑backs (`owl‑alpha`, `deepseek‑v4‑flash`) | Ollama, OpenRouter |
| **Tool orchestration** | 40+ built‑in toolsets (web, browser, terminal, file, vision, cron, delegation, etc.) | Python, `tools/` registry |
| **Persistent memory** | 5‑layer stack (Honcho vector store, Redis cache, SQLite FTS5, Obsidian vault, built‑in compact memory) | Honcho, pgvector, Redis, SQLite |
| **Task scheduling** | `cronjob` subsystem (26 jobs, < 1 s latency) | SQLite cron DB, `cronjob` tool |
| **Sub‑agent delegation** | `delegate_task` (max 3 parallel children) for heavy workloads | Separate terminal sessions, isolated state |
| **Collaboration board** | Kanban board (`kanban` toolset) for multi‑profile workstreams | SQLite kanban DB |
| **Gateway** | Multi‑platform messaging (Telegram, Discord, Slack, etc.) | Hermes gateway, platform adapters |
| **Security** | Secret redaction, PII masking, manual approvals for destructive commands | `approvals.mode = manual` |

*... (rest of article omitted for brevity; full content is in the repository)*
