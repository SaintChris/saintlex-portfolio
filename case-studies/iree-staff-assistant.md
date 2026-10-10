# IREE Staff Assistant and Website Chat

Status: Production pilot

## Problem

Staff at IREE Solar answer a lot of product questions: inverter limits, battery specs, warranty terms. The answers sit in dozens of manufacturer datasheets and manuals, some of them scanned images or in other languages. Customers ask similar questions, but a public chatbot that guesses about prices or warranties would cause more trouble than it saves.

## What I built

Two assistants on one small server.

The staff assistant answers from 32 product documents. Search combines keyword and meaning-based matching, then a reranker picks the best passages. The prompt asks for exact figures, the right table column for the model asked about, and both values when two sources disagree. Staff can use it in the browser or a phone app.

The website chat answers customers only from a reviewed set of public company facts. Every answer has to cite an approved page, or the visitor gets a referral to the team instead. A guard blocks obvious prompt-injection attempts before the model sees them. A second check replaces any reply that quotes a price or repeats the hidden rules. The gateway keeps no transcripts or IP addresses.

To keep quality honest I wrote a fixed set of real product questions (51 at last count) and rerun it after any change to documents, settings or prompts. When I tried a different embedding model, the score dropped, so I reverted it.

## Diagram components

```text
Website visitor
  -> Website chat widget
  -> Public chat gateway (rate limits, input and output guards, fixed model and fact set)
  -> Assistant platform (restricted service account)
  -> Reviewed public facts
  -> Hosted LLM (per-visitor and daily limits, fallback model)

Staff (browser or phone app)
  -> Access gateway (sign-in, path allowlist)
  -> Assistant platform
  -> Document retrieval (hybrid search + reranker over product documents)
  -> Hosted LLM (per-person and team rate limits)

Operations
  CI builds and scans images -> deploy script with post-deploy checks
  Health check every 5 minutes
  Nightly encrypted backup to an on-site machine (restore drill tested)
```

## Stack

Open WebUI, Node.js gateway, Python, Docker Compose, Caddy, Cloudflare Access and Tunnel, ChromaDB, BM25 hybrid search with a cross-encoder reranker, GitHub Actions, Dependabot, Trivy, restic, a hosted LLM.

## My role

I designed, built and run all of it: the gateway, prompts, knowledge sets, server, access rules, backups and evaluations. I use AI coding agents for much of the code, and I review and test their changes before they ship.

## Status / what's next

The staff assistant runs as a pilot on the company server. The website chat is built into the redesigned company website, which is waiting on launch approval. Next: a table-aware document extractor, since wide spec tables split across chunks cause most of the remaining misses.
