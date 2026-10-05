"""Draws docs/img/34-models-cost-time.svg: cost and time per idea for every AI model we measured.

Numbers are the measured averages from scripts/eval_review.py (PROJECT_LOG.md steps 26-28).
Two separate panels (no shared axis), one row per model.
Run: python scripts/draw_model_chart.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "img" / "34-models-cost-time.svg"

# name, job, cost per idea (US cents), seconds per idea, right on unseen tests, in use?
MODELS = [
    ("Jev (TypeSafe)", "duplicate check", 0.03, 0.6, "70–71 / 71", True),
    ("Claude Haiku 4.5", "check + write up", 0.3, 2.3, "14 / 15", False),
    ("Claude Sonnet 5", "check + write up", 0.8, 3.8, "15 / 15", True),
    ("Claude Opus 5", "does everything", 4.6, 3.4, "23 / 23", False),
]

W, ROW, TOP = 1000, 56, 96
LABEL_W, PANEL_W, GAP = 200, 260, 36
X_COST = LABEL_W
X_TIME = X_COST + PANEL_W + GAP
X_ACC = X_TIME + PANEL_W + GAP
H = TOP + ROW * len(MODELS) + 64
BAR_H = 18
COST_MAX, TIME_MAX = 5.0, 4.0


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def bar(x0, value, vmax, y, used, label):
    w = max(2.0, (PANEL_W - 70) * value / vmax)
    r = min(4, w / 2)
    cls = "used" if used else "tried"
    # Rounded data-end, square at the baseline
    path = (f"M{x0},{y} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{BAR_H - 2 * r} "
            f"a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z")
    return (f'<path class="{cls}" d="{path}"><title>{esc(label)}</title></path>'
            f'<text class="val" x="{x0 + w + 8:.1f}" y="{y + 14}">{esc(label.split(": ")[1])}</text>')


parts = []
for i, (name, job, cost, secs, acc, used) in enumerate(MODELS):
    y = TOP + i * ROW
    parts.append(f'<text class="name" x="0" y="{y + 10}">{esc(name)}</text>')
    parts.append(f'<text class="job" x="0" y="{y + 28}">{esc(job)}{" · in use" if used else ""}</text>')
    parts.append(bar(X_COST, cost, COST_MAX, y, used, f"{name} cost per idea: {cost:g}¢"))
    parts.append(bar(X_TIME, secs, TIME_MAX, y, used, f"{name} time per idea: {secs:g} s"))
    parts.append(f'<text class="acc" x="{X_ACC}" y="{y + 14}">{esc(acc)}</text>')

baseline_h = ROW * len(MODELS) - (ROW - BAR_H) + 8
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
  aria-label="Cost and time per idea for each AI model tested. Jev 0.03 cents and 0.6 s, Claude Haiku 4.5 0.3 cents and 2.3 s, Claude Sonnet 5 0.8 cents and 3.8 s, Claude Opus 5 4.6 cents and 3.4 s.">
<style>
  svg {{ --bg:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#8a8984; --rule:#e4e3df; --used:#2a78d6; --tried:#b9b8b2; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --bg:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#8f8e88; --rule:#383835; --used:#3987e5; --tried:#5e5d58; }}
  }}
  text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: var(--ink); }}
  .bg {{ fill: var(--bg); }}
  .title {{ font-size: 15px; font-weight: 700; }}
  .sub, .job, .note {{ font-size: 12px; fill: var(--ink2); }}
  .name {{ font-size: 14px; font-weight: 600; }}
  .val, .acc {{ font-size: 13px; fill: var(--ink); }}
  .used {{ fill: var(--used); }}
  .tried {{ fill: var(--tried); }}
  .rule {{ stroke: var(--rule); stroke-width: 1; }}
  .key {{ font-size: 12px; fill: var(--ink2); }}
</style>
<rect class="bg" width="{W}" height="{H}" rx="8"/>
<g transform="translate(24,0)">
  <text class="title" x="{X_COST}" y="34">Cost per idea</text>
  <text class="sub" x="{X_COST}" y="52">US cents · lower is better</text>
  <text class="title" x="{X_TIME}" y="34">Time per idea</text>
  <text class="sub" x="{X_TIME}" y="52">seconds · lower is better</text>
  <text class="title" x="{X_ACC}" y="34">Right on unseen tests</text>
  <text class="sub" x="{X_ACC}" y="52">its own job</text>
  <line class="rule" x1="{X_COST}" y1="{TOP - 8}" x2="{X_COST}" y2="{TOP - 8 + baseline_h}"/>
  <line class="rule" x1="{X_TIME}" y1="{TOP - 8}" x2="{X_TIME}" y2="{TOP - 8 + baseline_h}"/>
  {''.join(parts)}
  <rect class="used" x="0" y="{H - 34}" width="12" height="12" rx="2"/>
  <text class="key" x="18" y="{H - 24}">in use today</text>
  <rect class="tried" x="110" y="{H - 34}" width="12" height="12" rx="2"/>
  <text class="key" x="128" y="{H - 24}">tested, not chosen</text>
  <text class="note" x="{X_TIME}" y="{H - 24}">Measured with scripts/eval_review.py, October 2026</text>
</g>
</svg>
"""
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT}")
