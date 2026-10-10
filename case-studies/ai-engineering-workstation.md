# AI-Assisted Engineering Workstation

Status: Personal tooling

## Problem

I do most of my building with AI coding agents (Claude Code and Codex). Out of the box they forget context between sessions and can run destructive commands without warning. My notes, tasks and code also kept drifting into duplicate copies across tools. I wanted one setup where agents can help with real work without making a mess.

## What I built

- Notes live in an Obsidian vault, tasks in Super Productivity, code in Git repositories. Each project has a README with its status and next step.
- A small service on my Mac indexes the vault so agents can search past decisions and notes. Agents get read-only access, and private folders are never indexed.
- A scheduled job rebuilds my priorities page from the project READMEs and flags misplaced files, projects without a proper README, and a stale search index. It reports problems and never moves or deletes notes.
- I run a patched build of Super Productivity with a local REST API, and I've added endpoints to it, such as logging time on a given day. Agents can read and update tasks, and a hook syncs task status when a session ends.
- A mod holds risky shell commands (recursive deletes, hard resets, force pushes, migrations), shows what they would change, and waits for me to approve or cancel. Other mods add a status line and a progress panel for multi-agent builds.
- For large jobs, a lead agent plans the work and hands parts to worker agents in separate Git worktrees. Then it reviews what comes back.
- A dotfiles repository holds a health check and a names-only inventory, so I can rebuild the setup without copying secrets.

## Stack

macOS, zsh, Python, TypeScript, SQLite full-text search, launchd, MCP, Claude Code, Codex, Obsidian, Super Productivity, Git and GitHub.

## My role

I designed and built it for my own use. It's the environment I use for my day-to-day work.

## Status / what's next

In daily use. One open issue: the command guard didn't fire in one long-running background session, though it worked in fresh ones. I haven't found the cause yet, so I test any change to it in a new session.
