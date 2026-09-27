# Tapwise (NFC Idea Finder) — read this first

Read these two files before doing anything else:
- **PROJECT_LOG.md** — the whole story so far, in order, step by step, written simply. This is the real source of truth for *why* things are the way they are.
- **RUN.md** — how to run it locally and how it's deployed on the user's Raspberry Pi (Docker).

## What this project is

A Flask + SQLite website ("Tapwise") that asks visitors questions about their everyday life and suggests NFC tag ideas that fit, with credit to whoever shared the idea (YouTube/Reddit creators, or other visitors), a link to buy the right tag, and setup steps. It's also a growing **community idea bank**: visitors can add their own ideas via a suggestion form, an admin (the user) reviews and approves them at `/admin`, and approved ideas show up credited with the visitor's name. People can also mark an idea "I use this" to help good ideas rise to the top.

## Architecture, quick version

- `app/app.py` — Flask app: routes, matching, admin (HTTP basic auth via `ADMIN_PASSWORD` env var), duplicate-idea detection.
- `app/database.py` — SQLite. Curated content (`db/*.json`) is dropped & reloaded into SQLite on every start; visitor submissions and approved community ideas live only in SQLite and are never touched by that reload.
- `app/engines/` — the idea-ranking engines (`rules.py` is the one in use; `jev.py` is a placeholder for a hosted AI model, not usable on the Pi).
- `app/questions.py` — the branching quiz ("worlds" of everyday life).
- `app/tags.py` — matches an idea to which physical NFC tag to buy.
- `app/static/` — plain HTML/CSS/JS frontend (`index.html`, `app.js`, `style.css`, `admin.html`). No build step, no framework.
- `db/` — curated ideas, sources, tag profiles as JSON. `db/raw/` has the raw NotebookLM outputs these were built from; `scripts/build_db.py` builds the JSON from those (only re-run this if the user hands you new raw NotebookLM batches).

## Working style (important)

- the user is an ICT engineer and developer who builds with AI rather than hand-coding. Keep reports to him short: what was done and what he needs to decide or do. (PROJECT_LOG.md is different: it's written for a general audience, simply enough for a curious 14-year-old.)
- Move fast: skip formal test suites, ship working code, verify with a quick manual check (curl / a Playwright screenshot) rather than writing test files.
- **After any meaningful change**, add a new numbered entry to `PROJECT_LOG.md` (same style as the existing entries: what changed, why, a short lesson). This file becomes the public README's story, so write for a general audience, not just the user.
- the user cares about being transparent that this was built together with Claude — keep that framing in the log and README, don't erase it.
- Commit and push when done; the Pi deploys by `git pull` + Docker rebuild (see RUN.md), it does not auto-deploy.

## Data & credit rules (don't break these)

- Every curated idea must credit a real, checkable source (a real video/thread URL, or `s00` "Written by the Tapwise creator" for ideas written from general knowledge — never an invented source).
- Community (visitor-submitted) ideas are credited to the visitor by name (or "A Tapwise visitor" if they didn't opt in to credit).
- No content sourced from pirated/questionable sources (books from Anna's Archive were deliberately removed for this reason — see PROJECT_LOG.md step 19).
