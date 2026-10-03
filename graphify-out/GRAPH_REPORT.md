# Graph Report - nfc-idea-finder  (2026-10-03)

## Corpus Check
- 45 files · ~364,235 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .css 1)

## Summary
- 306 nodes · 497 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee9e7f2f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- database.py
- Day 1: Saturday 26 September 2026
- ai_review.py
- jev_lab.py
- app.js
- NFC Idea Finder: project log
- similar.py
- eval_review.py
- rules.py
- draw_hero_pixel.py
- Tapwise (NFC Idea Finder) — read this first
- raw/README.md
- deploy.sh

## God Nodes (most connected - your core abstractions)
1. `Day 1: Saturday 26 September 2026` - 33 edges
2. `connect()` - 16 edges
3. `esc()` - 11 edges
4. `run_ai_review()` - 10 edges
5. `reload_catalog()` - 9 edges
6. `admin_only()` - 9 edges
7. `renderIdea()` - 9 edges
8. `approve()` - 8 edges
9. `Tapwise (NFC Idea Finder) — read this first` - 8 edges
10. `NFC Idea Finder: project log` - 8 edges

## Surprising Connections (you probably didn't know these)
- `30. "Show the original words"` --references--> `similar()`  [INFERRED]
  PROJECT_LOG.md → app/app.py
- `Why Jev, and how we made it work` --references--> `dupes()`  [INFERRED]
  README.md → scripts/eval_review.py
- `Why Jev, and how we made it work` --references--> `route()`  [INFERRED]
  README.md → scripts/eval_review.py
- `ai_review_now()` --calls--> `enabled()`  [EXTRACTED]
  app/app.py → app/ai_review.py
- `start_ai_sweep()` --calls--> `enabled()`  [EXTRACTED]
  app/app.py → app/ai_review.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (19): admin_only(), admin_page(), ai_review_now(), _apps(), browse(), explore(), index(), match() (+11 more)

### Community 1 - "database.py"
Cohesion: 0.08
Nodes (30): ai_sweep(), approve(), catalog_fresh(), original_text(), reload_catalog(), run_ai_review(), safe_url(), set_status() (+22 more)

### Community 2 - "Day 1: Saturday 26 September 2026"
Cohesion: 0.05
Nodes (35): similar(), similar_ideas(), 10. New direction: local first, on a Raspberry Pi, 11. First working version, built in one go, 12. Version 2: ask about people's day, not about NFC, 13. Less text, more curiosity, 14. 22 Reddit threads, and a branching quiz, 15. A home-page illustration, drawn with code (+27 more)

### Community 3 - "ai_review.py"
Cohesion: 0.11
Nodes (16): claude_enabled(), claude_review(), claude_write(), _client(), Draft, _effort(), enabled(), _jev() (+8 more)

### Community 4 - "jev_lab.py"
Cohesion: 0.09
Nodes (10): _need_options(), _world_question(), idea(), tag(), analyse(), collect(), one(), decide() (+2 more)

### Community 5 - "app.js"
Cohesion: 0.19
Nodes (24): activeQuestions(), bank, esc(), facts(), init(), LABELS, linkTag(), loadBank() (+16 more)

### Community 6 - "NFC Idea Finder: project log"
Cohesion: 0.08
Nodes (21): Before going public (checklist), Lessons so far, NFC Idea Finder: project log, Open to-do list, Screenshot checklist (for the README), The idea in one paragraph, Timeline, Who built it, and how (+13 more)

### Community 7 - "similar.py"
Cohesion: 0.36
Nodes (3): Index, _stem(), tokens()

### Community 8 - "eval_review.py"
Cohesion: 0.12
Nodes (4): Why Jev, and how we made it work, dupes(), route(), split()

### Community 9 - "rules.py"
Cohesion: 0.17
Nodes (6): rank(), score_fit(), collect_needs(), _feasibility(), rank(), _smart_home_need()

### Community 10 - "draw_hero_pixel.py"
Cohesion: 0.16
Nodes (11): box(), P(), box(), bubble(), disc(), hexc(), P(), poly() (+3 more)

### Community 11 - "Tapwise (NFC Idea Finder) — read this first"
Cohesion: 0.22
Nodes (8): Architecture, quick version, Data & credit rules (don't break these), graphify, Private until the user says "go public" (hard rule), Tapwise (NFC Idea Finder) — read this first, The main goal (more important than the idea bank itself), What this project is, Working style (important)

## Knowledge Gaps
- **58 isolated node(s):** `state`, `LABELS`, `bank`, `deploy.sh script`, `Private until the user says "go public" (hard rule)` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 138 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Day 1: Saturday 26 September 2026` connect `Day 1: Saturday 26 September 2026` to `NFC Idea Finder: project log`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `similar()` connect `Day 1: Saturday 26 September 2026` to `app.py`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **What connects `state`, `LABELS`, `bank` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07948717948717948 - nodes in this community are weakly interconnected._
- **Should `database.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08019323671497584 - nodes in this community are weakly interconnected._
- **Should `Day 1: Saturday 26 September 2026` be split into smaller, more focused modules?**
  _Cohesion score 0.05405405405405406 - nodes in this community are weakly interconnected._
- **Should `ai_review.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._