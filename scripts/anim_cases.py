"""Build docs/anim/cases.json: the real data behind the README animation (docs/anim/pipeline.html).

Jev's numbers are its recorded lab answers (scripts/lab_results), put through the live rule from app/ai_review.py.
Claude's part is one real call to the live claude_write() per case that Jev hands over. Run it once, in the container:
    docker exec -i tapwise python - < scripts/anim_cases.py > docs/anim/cases.json
Fails loudly instead of writing anything it can't back up."""
import json
import os
import sys
import time

ROOT = "/srv" if os.path.isdir("/srv/app") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "app"))
import ai_review              # noqa: E402
import database               # noqa: E402
from questions import NEEDS   # noqa: E402

CASES = [  # (lab file, exact visitor text)
    ("TUNE", "tag on the kettle that starts a 4 minute tea timer"),
    ("NEAR", "tag on the shower wall that starts a 5-minute timer to save water"),
    ("TUNE", "tag on the beehive that logs each inspection and honey harvest"),
]
SONNET_PRICE = (2, 10)        # $ per million tokens (input, output), as in scripts/eval_review.py
SOURCES = {
    "jev_cost": "README 'What it costs': measured average of one Jev duplicate check over the test ideas",
    "per_1000": "README 'What it costs': 1,000 visitor ideas, half duplicates; Opus 5 doing everything vs "
                "Jev on all 1,000 + Sonnet 5 on the 500 new ones and ~70 unsure duplicates",
}


def fail(msg):
    sys.exit(f"anim_cases: {msg}")


def jev_decision(rec):
    """The live rule (ai_review.jev_find_duplicate) applied to recorded answers: shortlist wording C + 'covers'."""
    short = rec["short"]["C"]
    top = sorted(((k, p) for k, p in short.items() if k != "none"), key=lambda x: -x[1])[:ai_review.SHORTLIST]
    rows = []
    for iid, p in top:
        covers = None
        if p >= ai_review.PICK_MIN:
            if iid not in rec["pairs"] or "covers" not in rec["pairs"][iid]:
                fail(f"no recorded side-by-side answer for {iid} on {rec['text']!r}")
            covers = rec["pairs"][iid]["covers"]
        rows.append({"id": iid, "pick": p, "covers": covers})
    best = max((r for r in rows if r["covers"] is not None and r["covers"] >= ai_review.COVERS_MIN),
               key=lambda r: r["covers"], default=None)
    sure = bool(best) and best["pick"] >= ai_review.SURE_PICK and best["covers"] >= ai_review.SURE_COVERS
    return {"shortlist": rows, "none": short.get("none", 0.0),
            "match": best["id"] if best else None, "sure": sure,
            "outcome": "duplicate_by_jev" if sure else ("unsure_to_claude" if best else "new_to_claude")}


def main():
    database.load_content()
    bank = [{"id": i["id"], "title": i["title"], "summary": i["summary"], "place": i.get("place"),
             "result": i.get("result")} for i in database.get_catalog()["ideas"] if i["status"] != "hidden"]
    by_id = {i["id"]: i for i in bank}
    needs = [{"id": n["id"], "label": n["label"]} for n in NEEDS]
    labs = {}
    out = []
    for lab, text in CASES:
        if lab not in labs:
            labs[lab] = json.load(open(os.path.join(ROOT, "scripts", "lab_results", f"{lab}.json")))
        rec = next((r for r in labs[lab] if r["text"] == text), None)
        if not rec:
            fail(f"{text!r} not in {lab}.json")
        jev = jev_decision(rec)
        for r in jev["shortlist"]:
            if r["id"] not in by_id:
                fail(f"{r['id']} is not in the idea bank")
            r["title"] = by_id[r["id"]]["title"]
        case = {"lab": lab, "text": text, "expected": rec["expected"], "jev": jev, "claude": None}
        if jev["outcome"] != "duplicate_by_jev":
            copy = by_id[jev["match"]] if jev["match"] else None
            t0 = time.time()
            w = ai_review.claude_write(text, None, needs, possible_copy=copy)
            if not w:
                fail(f"Claude call failed for {text!r}")
            tin, tout = w["usage"]["input_tokens"], w["usage"]["output_tokens"]
            case["claude"] = {
                "model": ai_review.WRITER_MODEL, "verdict": w["verdict"], "confidence": w["confidence"],
                "reason": w["reason"], "draft": w["draft"], "possible_copy": copy["id"] if copy else None,
                "input_tokens": tin, "output_tokens": tout, "seconds": round(time.time() - t0, 2),
                "cost_usd": (tin * SONNET_PRICE[0] + tout * SONNET_PRICE[1]) / 1e6}
            if w["verdict"] == "new" and not (w["draft"] and w["draft"].get("title")):
                fail(f"Claude said new but wrote no title for {text!r}")
        print(f"{text[:50]:<50} -> {jev['outcome']}" + (f", Claude: {case['claude']['verdict']}" if case["claude"] else ""),
              file=sys.stderr)
        out.append(case)
    if [c["jev"]["outcome"] for c in out] != ["duplicate_by_jev", "unsure_to_claude", "new_to_claude"]:
        fail("the three cases no longer show the three routes the animation tells; pick other cases")
    json.dump({
        "built": time.strftime("%Y-%m-%d"),
        "rule": {"pick_min": ai_review.PICK_MIN, "covers_min": ai_review.COVERS_MIN,
                 "sure_pick": ai_review.SURE_PICK, "sure_covers": ai_review.SURE_COVERS},
        "bank_size": len(bank),
        "ideas": {iid: by_id[iid]["title"] for iid in sorted({r["id"] for c in out for r in c["jev"]["shortlist"]})},
        "cases": out,
        "jev_cost": {"usd": 0.0003, "seconds": 0.6, "source": SOURCES["jev_cost"]},
        "per_1000": {"opus_alone_usd": 46.0, "jev_plus_sonnet_usd": 4.60, "source": SOURCES["per_1000"]},
    }, sys.stdout, indent=2, ensure_ascii=False)


main()
