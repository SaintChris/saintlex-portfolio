# Solar and Battery Performance Reporting

Status: Professional work

## Problem

Customers and the service team ask questions like "why is my battery charging from the grid?" or "why does the app show no solar today?" The answers are in the monitoring portal for each Tesla system, but reading them by hand takes time. It's also easy to mistake a reporting gap for an equipment fault. API access hadn't been issued yet, so any tool had to work with the portal as it is.

## What I built

A repeatable process that turns one site and one date range into two PDF reports.

- A read-only script runs inside my signed-in portal session and pulls daily energy totals, 15-minute power data, one-minute grid status, battery state of charge, alerts and site settings.
- Daily load and solar figures must add up to the period totals before the data is used. Grid outages are found from the one-minute grid status, not guessed from gaps.
- The customer report covers status, energy, charts, alerts and plain next steps. The internal report adds service tickets, the full alert log, settings and firmware, and is marked not for customer distribution.
- Every number comes from the collected data. No estimates of system size, tariffs or savings. Confirmed facts stay separate from things that aren't established. A telemetry fault isn't treated as proof of a solar fault, and battery behaviour is read against the site's battery mode and backup reserve, not blamed on load alone.

## Stack

Tesla Powerhub, JavaScript, Python, ReportLab, matplotlib, JSON, Google Drive.

## My role

I built the collector, the report layouts and the findings rules, and I write and check each report. Reports go out only after review.

## Prototype: operations dashboard

Before this, I built a read-only operations dashboard prototype for solar, battery, grid and connectivity monitoring. It runs only on simulated telemetry plus public weather and solar references, and no customer equipment is connected. Its main rule: missing, stale or conflicting data is never shown as healthy or as zero production. It has sign-in with read-only roles and no equipment control of any kind. Built with FastAPI, a TypeScript web console, SQLite or PostgreSQL, and Alembic.

## Status / what's next

The report process has been used for a few customer sites. When API access is issued, the collection step switches to the official API. I've already mapped each query to its API endpoint, so the report steps stay the same.
