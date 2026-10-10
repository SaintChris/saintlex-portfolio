# IREE Solar Website Redesign

Status: Professional work — launch pending

## Problem

IREE Solar's website needed a redesign that explains its solar, battery and water services clearly and sends each enquiry to the right form. It had to stay on Squarespace so the team can keep editing it. Every claim on the site had to be one the company had approved.

## What I built

A redesign of 15 pages, plus site-wide styles and scripts that apply to all 20 pages on the site.

The custom CSS, footer code and page code blocks are built from one Git repository, not edited by hand in Squarespace. After each save I read the page back and compare it with the build, so I know the saved site matches the source.

I moved motion and layout work out of JavaScript and into CSS, with reduced-motion fallbacks and a pause control. Scripts handle what CSS can't, such as menu keyboard handling and cleanup when Squarespace swaps content.

The interactive parts are small. There's a FAQ search, a filtered project gallery that works from the keyboard, and a guided enquiry path that pre-fills the right form. The three enquiry forms stay native Squarespace forms and save to Google Sheets, so no secrets sit on the public site. The customer chat from the staff assistant project is embedded on every page, pinned to a known version of the widget.

Checks ran at seven screen widths on every page for overflow, headings and layout, plus interaction tests for the menu, gallery and enquiry paths. A later code review found two bugs on the saved site, a FAQ filter that could hide answers and a chat retry limit that never reset. I fixed both and added regression checks.

## Stack

Squarespace 7.1, Tailwind CSS, TypeScript, Vite, JavaScript, Git and GitHub, Google Sheets, browser-based layout and interaction checks.

## My role

I wrote the redesign spec from the manager's notes, built the source, saved and verified every page, and applied the approved copy. AI coding agents did much of the implementation under my direction. I checked the results against the rendered site before anything was saved.

## Status / what's next

The redesign is complete and password-protected while it waits for launch approval. Before launch: test the forms end to end, check on real phones, and set up redirects from the old pages.
