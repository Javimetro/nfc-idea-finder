# Tapwise (NFC Idea Finder) — read this first

Read these two files before doing anything else:
- **PROJECT_LOG.md** — the whole story so far, in order, step by step, written simply. This is the real source of truth for *why* things are the way they are.
- **RUN.md** — how to run it locally and how it's deployed on the user's Raspberry Pi (Docker).

## Private until the user says "go public" (hard rule)

Tapwise stays private until the user explicitly says "go public". Until then:
- Don't publish it anywhere: no domain, no Cloudflare Tunnel, no port forwarding, no public hosting.
- It's only reachable on the user's home network and over Tailscale.
- The GitHub repo stays private.
- Don't build Turnstile, rate limits or other public-launch work unless the user asks. Mentioning it is fine.
- If a task would make the site reachable from the internet, stop and ask the user first.

## The main goal (more important than the idea bank itself)

the user's main goal for this repo: **show a human staying in the AI loop and picking the right model for each task**, with measured evidence (accuracy, cost, speed) behind every choice. The NFC idea bank is the vehicle for that.
- **Jev (TypeSafe) gets special prominence** in the README and log: the user chose it for the duplicate check because it's very cheap for that job, and wanted to try an innovative model. Keep that story front and centre.
- Any change of model, or of how a model is used, gets measured first with `scripts/eval_review.py` on `scripts/review_cases.py` (tune on DEV, score HOLDOUT once), and the numbers go in PROJECT_LOG.md and the README's model table.
- Default to the cheapest model that measures "good enough" for the task, and say why.

## What this project is

A Flask + SQLite website ("Tapwise") that asks visitors questions about their everyday life and suggests NFC tag ideas that fit, with credit to whoever shared the idea (YouTube/Reddit creators, or other visitors), a link to buy the right tag, and setup steps. It's also a growing **community idea bank**: visitors can add their own ideas via a suggestion form, AI reviews them automatically (Jev checks for duplicates, Claude checks and writes up new ones; `app/ai_review.py`), every decision is listed at `/admin` with undo, and approved ideas show up credited with the visitor's name. People can also mark an idea "I use this" to help good ideas rise to the top.

## Architecture, quick version

- `app/app.py` — Flask app: routes, matching, admin (HTTP basic auth via `ADMIN_PASSWORD` env var), duplicate-idea detection.
- `app/database.py` — SQLite. Curated content (`db/*.json`) is dropped & reloaded into SQLite on every start; visitor submissions and approved community ideas live only in SQLite and are never touched by that reload.
- `app/ai_review.py` — the AI review of visitor ideas: Jev (duplicates) + Claude Sonnet 5 (real/safe? write it up); Claude-only fallback.
- `app/engines/` — the idea-ranking engines for the quiz (`rules.py` is the one in use; `jev.py` is a placeholder).
- `app/questions.py` — the branching quiz ("worlds" of everyday life).
- `app/tags.py` — matches an idea to which physical NFC tag to buy.
- `app/static/` — plain HTML/CSS/JS frontend (`index.html`, `app.js`, `style.css`, `admin.html`). No build step, no framework.
- `db/` — curated ideas, sources, tag profiles as JSON. `db/raw/` has the raw NotebookLM outputs these were built from; `scripts/build_db.py` builds the JSON from those (only re-run this if the user hands you new raw NotebookLM batches).

## Working style (important)

- the user is an ICT engineer and developer who builds with AI rather than hand-coding. Keep reports to him short: what was done and what he needs to decide or do. (PROJECT_LOG.md is different: it's written for a general audience, simply enough for a curious 14-year-old.)
- Move fast: skip formal test suites, ship working code, verify with a quick manual check (curl / a Playwright screenshot) rather than writing test files.
- **After any meaningful change**, add a new numbered entry to `PROJECT_LOG.md` (same style as the existing entries: what changed, why, a short lesson). This file becomes the public README's story, so write for a general audience, not just the user.
- the user cares about being transparent that this was built together with Claude — keep that framing in the log and README, don't erase it.
- Commit and push when done, then deploy on the Pi yourself with `scripts/deploy.sh` (pull + Docker rebuild + health check; secrets come from `~/tapwise.env`, which only the user edits). If that file is missing, tell the user the one-time command in RUN.md.

## Data & credit rules (don't break these)

- Every curated idea must credit a real, checkable source (a real video/thread URL, or `s00` "Written by the Tapwise creator" for ideas written from general knowledge — never an invented source).
- Community (visitor-submitted) ideas are credited to the visitor by name (or "A Tapwise visitor" if they didn't opt in to credit).
- No content sourced from pirated/questionable sources (books from Anna's Archive were deliberately removed for this reason — see PROJECT_LOG.md step 19).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- **Before every commit that gets pushed, run `graphify update .` and include `graphify-out/graph.json` + `GRAPH_REPORT.md` in the commit**, so the graph on GitHub always matches the code.
- the user won't type graphify commands. Use graphify on your own whenever it helps answer his questions (how something works, what a change would affect, where something lives), and answer in plain words.
- If the map changes a lot, refresh the README screenshot `docs/img/31-graphify-map.png` (Playwright in Docker, image `tapwise-ui`, open `graphify-out/graph.html`, wait ~20 s, 1600×1000).
