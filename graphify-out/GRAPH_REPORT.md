# Graph Report - nfc-idea-finder  (2026-10-03)

## Corpus Check
- 48 files · ~394,353 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .css 1)

## Summary
- 325 nodes · 529 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a5cc874`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- database.py
- Day 1: Saturday 26 September 2026
- ai_review.py
- eval_review.py
- app.js
- Tapwise: NFC ideas, reviewed by Jev + Claude
- draw_hero.py
- review_cases_big.py
- render_animation.py
- draw_hero_pixel.py
- Tapwise (NFC Idea Finder) — read this first
- raw/README.md
- deploy.sh
- jev_lab.py

## God Nodes (most connected - your core abstractions)
1. `Day 1: Saturday 26 September 2026` - 35 edges
2. `connect()` - 16 edges
3. `esc()` - 11 edges
4. `run_ai_review()` - 10 edges
5. `reload_catalog()` - 9 edges
6. `admin_only()` - 9 edges
7. `renderIdea()` - 9 edges
8. `Tapwise: NFC ideas, reviewed by Jev + Claude` - 9 edges
9. `approve()` - 8 edges
10. `Tapwise (NFC Idea Finder) — read this first` - 8 edges

## Surprising Connections (you probably didn't know these)
- `30. "Show the original words"` --references--> `similar()`  [INFERRED]
  PROJECT_LOG.md → app/app.py
- `Why Jev, and how we made it work` --references--> `dupes()`  [INFERRED]
  README.md → scripts/eval_review.py
- `Why Jev, and how we made it work` --references--> `route()`  [INFERRED]
  README.md → scripts/eval_review.py
- `reload_catalog()` --calls--> `Index`  [EXTRACTED]
  app/app.py → app/similar.py
- `ai_review_now()` --calls--> `enabled()`  [EXTRACTED]
  app/app.py → app/ai_review.py

## Import Cycles
- None detected.

## Communities (15 total, 3 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (20): enabled(), admin_only(), admin_page(), ai_review_now(), _apps(), browse(), explore(), index() (+12 more)

### Community 1 - "database.py"
Cohesion: 0.08
Nodes (30): ai_sweep(), approve(), catalog_fresh(), original_text(), reload_catalog(), run_ai_review(), safe_url(), set_status() (+22 more)

### Community 2 - "Day 1: Saturday 26 September 2026"
Cohesion: 0.05
Nodes (37): similar(), similar_ideas(), 10. New direction: local first, on a Raspberry Pi, 11. First working version, built in one go, 12. Version 2: ask about people's day, not about NFC, 13. Less text, more curiosity, 14. 22 Reddit threads, and a branching quiz, 15. A home-page illustration, drawn with code (+29 more)

### Community 3 - "ai_review.py"
Cohesion: 0.12
Nodes (15): claude_enabled(), claude_review(), claude_write(), _client(), Draft, _effort(), _jev(), jev_enabled() (+7 more)

### Community 4 - "eval_review.py"
Cohesion: 0.08
Nodes (10): _need_options(), _world_question(), Why Jev, and how we made it work, fail(), jev_decision(), main(), idea(), tag() (+2 more)

### Community 5 - "app.js"
Cohesion: 0.19
Nodes (24): activeQuestions(), bank, esc(), facts(), init(), LABELS, linkTag(), loadBank() (+16 more)

### Community 6 - "Tapwise: NFC ideas, reviewed by Jev + Claude"
Cohesion: 0.08
Nodes (23): Before going public (checklist), Lessons so far, NFC Idea Finder: project log, Open to-do list, Screenshot checklist (for the README), The idea in one paragraph, Timeline, Who built it, and how (+15 more)

### Community 7 - "draw_hero.py"
Cohesion: 0.16
Nodes (7): Index, _stem(), tokens(), box(), P(), poly(), sticker()

### Community 9 - "render_animation.py"
Cohesion: 0.10
Nodes (9): rank(), score_fit(), collect_needs(), _feasibility(), rank(), _smart_home_need(), capture(), embed() (+1 more)

### Community 10 - "draw_hero_pixel.py"
Cohesion: 0.33
Nodes (7): box(), bubble(), disc(), hexc(), P(), poly(), sticker()

### Community 11 - "Tapwise (NFC Idea Finder) — read this first"
Cohesion: 0.22
Nodes (8): Architecture, quick version, Data & credit rules (don't break these), graphify, Private until the user says "go public" (hard rule), Tapwise (NFC Idea Finder) — read this first, The main goal (more important than the idea bank itself), What this project is, Working style (important)

### Community 14 - "jev_lab.py"
Cohesion: 0.19
Nodes (6): analyse(), collect(), one(), decide(), option_text(), score()

## Knowledge Gaps
- **61 isolated node(s):** `state`, `LABELS`, `bank`, `deploy.sh script`, `Private until the user says "go public" (hard rule)` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 148 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Day 1: Saturday 26 September 2026` connect `Day 1: Saturday 26 September 2026` to `Tapwise: NFC ideas, reviewed by Jev + Claude`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `similar()` connect `Day 1: Saturday 26 September 2026` to `app.py`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **What connects `state`, `LABELS`, `bank` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08097165991902834 - nodes in this community are weakly interconnected._
- **Should `database.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07890070921985816 - nodes in this community are weakly interconnected._
- **Should `Day 1: Saturday 26 September 2026` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._
- **Should `ai_review.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11822660098522167 - nodes in this community are weakly interconnected._