# A Local, Privacy-First Memory Service for AI Assistants

## Status

Personal system, running on one Mac and used daily by several AI coding assistants. The source repository is private until its history has been reviewed for personal data; this case study describes the design.

## Problem

I use more than one AI assistant. Each started every session without context, and the obvious fix, pasting notes into prompts or giving every tool access to the whole notes vault, would have exposed personal and work records to every model and every log.

The goal was one shared memory that any approved assistant can search, built from my own notes, where private material cannot leak in by accident.

## Design

```text
Obsidian vault (canonical, human-edited)
    ↓  nightly index: allowlisted folders only
memoryd  (localhost-only FastAPI + SQLite)
    ├── documents and chunks (full-text search, optional local embeddings)
    ├── threads → sessions → messages (conversation continuity)
    └── durable memories (facts, preferences, corrections), each with provenance
    ↓
Read-only MCP server → AI assistants
```

- **Notes stay canonical.** The database is derived and can be rebuilt from the vault at any time.
- **Loopback only.** The server refuses to bind anywhere except `127.0.0.1`, `localhost` or `::1`, and every API route requires a bearer token compared in constant time.
- **Read-only by default.** The MCP tools assistants see can search and read. Write tools exist only when explicitly enabled, and only for models whose tool use has been verified for that exact version.
- **Retrieved text is data, not instructions.** The MCP server tells clients that memory evidence never grants authority.

## Privacy controls

Privacy fails closed at three levels:

1. **Folder.** `Private/`, `Archive/` and `Journal/` are never indexed, whatever a note's metadata says. A forgotten tag cannot leak a note.
2. **Metadata.** Inside indexed folders, a note is excluded if its frontmatter marks it private or restricted, or if that frontmatter is malformed, duplicated or ambiguous. Unknown values are treated as restricted, never guessed.
3. **Content.** Notes whose names or text look like credentials (private keys, cloud access keys, token assignments) are skipped.

When a note becomes restricted later, every earlier indexed version and its embeddings are purged too, so history queries cannot recover it. Symlinked folders are not followed out of the vault.

## Operations

- A nightly job regenerates the priorities note from project READMEs, re-indexes the vault, and writes a health report. The report covers stale index age, misplaced files and broken links. It only reports; it never moves or deletes notes.
- Every indexing run writes an audit event, and every document and chunk carries a provenance record back to its source note and checksum.
- An automated pytest suite covers privacy exclusion (including malformed and ambiguous frontmatter), idempotent re-indexing, provenance, and the default folder rules.

## What went wrong, and what changed

- **The index went stale for 25 days** because nothing scheduled a refresh. Assistants were answering from three-week-old notes. Fix: the nightly job, plus an index-age check in the health report.
- **Folder moves exposed a gap in tag-based privacy.** During a vault reorganisation I found that two sensitive records had been searchable while they sat in a project folder. Fix: privacy by folder first, metadata second.
- **Over-broad "historical" rules.** A blanket rule marks two whole knowledge folders as historical, which hides useful notes from default searches. Next step: replace the folder rule with per-note status.

## Stack

Python 3.11, FastAPI, SQLite (FTS5), Ollama for local embeddings (`nomic-embed-text`), the MCP Python SDK, launchd, pytest.
