---
title: "I Built an AI Agent to Track My Job Applications. Here's What Broke — And How I Fixed It."
date: 2026-06-08
tags: ["Agentic AI", "MLOps", "Automation", "Production Systems"]
---

# I Built an AI Agent to Track My Job Applications. Here's What Broke — And How I Fixed It.

I track every job application in a Google Sheet. Company, role, date, status, notes. Simple.

The problem: I was updating it manually. Every few days, I'd remember to check my sent folder, scan for new applications, copy them into the sheet. I'd miss things. Status changes would sit in my inbox for a week before I noticed.

So I built an AI agent to do it for me.

## The Setup

The system runs on Hermes Agent on a single M1 Mac. Every 4 hours, a cron job fires and the agent scans Outlook Sent for new applications, scans Inbox, Junk, and Spam for responses, searches Gmail, reads the current Google Sheet, adds new rows, updates status changes, and sends a Telegram summary if anything changed.

All of it runs through Zapier MCP — no custom API code, no OAuth tokens to manage. Zapier handles authentication for Outlook, Gmail, Google Sheets, and Telegram.

## What Broke

The cron job was running. The status said "ok." But the sheet wasn't updating.

**Problem 1: Wrong API path.** The agent was looking for a local OAuth token file (`~/.hermes/google_token.json`) that didn't exist. It was trying to use the Google API directly instead of going through Zapier, which already had Google Sheets connected and authenticated.

**Problem 2: Unknown action names.** Even when the agent tried Zapier, it didn't know the exact action keys. Zapier's actions aren't guessable — `google_sheets_create_spreadsheet_row` isn't something you can infer. The agent was guessing, failing, and falling back to the non-existent token file.

**Problem 3: Outlook folder IDs.** The agent was passing "Sent" as the folder ID. Zapier needs the actual folder ID — a long encoded string. Without it, the search returned nothing.

**Problem 4: Zapier follow-up questions.** Zapier's write actions ask follow-up questions about formatting — bold, italic, colors. In an automated context, nobody answers them. The calls timed out.

## The Fix

Four specific changes to the cron job prompt:

1. **Call `list_enabled_zapier_actions` first.** Returns exact action keys for every connected app. No guessing.

2. **Use `COL$A`, `COL$B` for column mapping.** The sheet has no header row — first row is data. Zapier was reading "Bioprist Group" as the column name. Using `COL$A`, `COL$B` maps directly to spreadsheet columns.

3. **Include all formatting params.** Every write call now includes `text_format_bold: false`, `text_format_italic: false`, `background_color: "#FFFFFF"`. No stalled follow-up questions.

4. **Expand email search to all folders.** Inbox, Sent, Junk Email, and Spam. Job responses get filtered into Junk constantly.

## The Result

After the fix, one manual run found 7 untracked applications:

- **Talentoma** — Remote IT Support Assistant (LinkedIn, June 8)
- **Experfy** — Tech Support Associate Contractor (LinkedIn, June 7)
- **Vintti** — Computer Vision & ML Expert for AI Training (LinkedIn, June 4)
- **Anedot** — Customer Support Specialist (Gusto, June 8) — Rejected
- **Reboot Monkey** — Data Center Technician, Kingston (LinkedIn, June 8)
- **PurpleDot Logistics** — Freelance Pickup Personnel (LinkedIn, June 8)
- **OneVision Resources** — IT Spec (Outlook, June 8) — Rejected after AI role-play interview

Sheet went from 58 to 75 rows. The cron now runs automatically every 4 hours.

## Why This Matters

This isn't a demo. This is a production system using free-tier AI models, zero cloud cost, handling real email and real API calls — and recovering from errors I didn't anticipate.

Demos work when everything goes right. Infrastructure works when things break. And things always break.