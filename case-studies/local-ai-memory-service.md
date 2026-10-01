# A local, privacy-first memory service for AI assistants

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

The notes stay the source of truth. The database is derived from them, so I can delete it and rebuild it from the vault whenever I want.

The server only listens on the loopback address; it refuses to start on anything else. Every API call needs a bearer token, compared in constant time.

Assistants get read-only tools by default. Write tools have to be switched on, and even then only for a model version whose tool use I've actually tested. Anything the memory returns is treated as data. It never counts as an instruction.

## Privacy controls

Privacy fails closed at three levels:

1. By folder. `Private/`, `Archive/` and `Journal/` are never indexed, whatever a note's metadata says. Forget a tag and nothing leaks.
2. By metadata. Inside the indexed folders, a note is dropped if its frontmatter says private or restricted. It's also dropped if the frontmatter is broken or contradicts itself. Unknown values count as restricted.
3. By content. Anything whose name or text looks like a credential (private keys, cloud access keys, tokens) is skipped.

When a note becomes restricted later, every earlier indexed version and its embeddings are purged too, so history queries cannot recover it. Symlinked folders are not followed out of the vault.

## Operations

- A nightly job regenerates the priorities note from project READMEs, re-indexes the vault, and writes a health report. The report covers stale index age, misplaced files and broken links. It only reports; it never moves or deletes notes.
- Every indexing run writes an audit event, and every document and chunk carries a provenance record back to its source note and checksum.
- An automated pytest suite covers privacy exclusion (including malformed and ambiguous frontmatter), idempotent re-indexing, provenance, and the default folder rules.

## What went wrong, and what changed

The index went stale for 25 days and I didn't notice. Nothing scheduled a refresh, so the assistants were quietly answering from three-week-old notes. Now a nightly job reindexes, and the health report shouts when the index gets old.

Tags alone weren't enough. While reorganising the vault I found two sensitive records that had been searchable the whole time, just because they lived in a project folder with the wrong metadata. That's why folder rules now come first and tags second.

One rule is still too blunt. It marks two entire knowledge folders as "historical", which hides useful notes from normal searches. I want to replace it with a status on each note.

## Stack

Python 3.11, FastAPI, SQLite (FTS5), Ollama for local embeddings (`nomic-embed-text`), the MCP Python SDK, launchd, pytest.
