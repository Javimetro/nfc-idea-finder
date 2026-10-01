"""Score the AI review on the made-up ideas in review_cases.py. Nothing is saved; it only prints.

Run inside the container (it has the keys and the idea bank):
    docker exec tapwise python /srv/scripts/eval_review.py dupes  dev|holdout|tune|test   # Jev duplicate check
    docker exec tapwise python /srv/scripts/eval_review.py writer dev|holdout claude-haiku-4-5,claude-sonnet-5
    docker exec tapwise python /srv/scripts/eval_review.py route  near             # Jev only: what goes to Claude
    docker exec tapwise python /srv/scripts/eval_review.py claude dev|holdout     # old way: Claude does everything

Tune only on dev. Run holdout once, at the end."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "app"))
sys.path.insert(0, HERE)
import ai_review              # noqa: E402
import database               # noqa: E402
from questions import NEEDS   # noqa: E402
from review_cases import DEV, HOLDOUT   # noqa: E402
from review_cases_big import NEAR, TEST, TUNE   # noqa: E402

PRICE = {  # $ per million tokens (input, output)
    "claude-haiku-4-5": (1, 5), "claude-sonnet-5": (2, 10), "claude-opus-5": (5, 25), "jev": (0.042, 0),
}


def bank():
    database.load_content()          # same as app start: curated JSON -> SQLite (visitor data untouched)
    cat = database.get_catalog()
    return [{"id": i["id"], "title": i["title"], "summary": i["summary"], "place": i.get("place"),
             "result": i.get("result")} for i in cat["ideas"] if i["status"] != "hidden"]


def dupes(cases, ideas):
    """Jev duplicate check only (no Claude). Cases: (text, expected, ids, [style]); ids may be "i015|i081"."""
    by_id = {i["id"]: i for i in ideas}
    tally, tokens, t0, n = {}, 0, time.time(), 0
    for case in cases:
        text, verdict, ids = case[:3]
        style = case[3] if len(case) > 3 else "plain"
        if verdict not in ("duplicate", "new", "?"):
            continue
        n += 1
        d = ai_review.jev_find_duplicate(text, None, ideas)
        if not d:
            print("FAILED:", text)
            continue
        tokens += d["details"]["input_tokens"]
        got = d["duplicate_of"]
        ok = (got in ids.split("|")) if verdict == "duplicate" else (got is None) if verdict == "new" else None
        if ok is not None:
            t = tally.setdefault(style, [0, 0])
            t[0] += ok
            t[1] += 1
        want = f"duplicate {ids}" if verdict == "duplicate" else verdict if verdict == "new" else f"? ({ids})"
        print(f"{'✓' if ok else '✗' if ok is False else ' '} {text[:72]:<72} want {want:<18} got {got or 'new'}")
        if ok is False:
            for r in d["details"]["shortlist"]:
                cov = "-" if r["covers"] is None else f"{r['covers']:.2f}"
                print(f"      {r['id']} {by_id[r['id']]['title'][:40]:<40} pick {r['pick']:.2f}  covers {cov}")
    right, graded = sum(t[0] for t in tally.values()), sum(t[1] for t in tally.values())
    print(f"\nJev duplicate check: {right}/{graded} right | by style: "
          + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(tally.items()))
          + f" | {(time.time() - t0) / n:.1f}s per idea | {tokens / n:.0f} tokens per idea"
          f" = ${tokens / n / 1e6 * PRICE['jev'][0]:.5f} per idea")


def route(cases, ideas):
    """Jev only (no Claude calls): which ideas Jev files alone, which go to Claude for a second look."""
    tally = {}
    for case in cases:
        text, verdict, ids = case[:3]
        if verdict not in ("duplicate", "new"):
            continue
        d = ai_review.jev_find_duplicate(text, None, ideas)
        if not d:
            continue
        if d["duplicate_of"] and d["sure"]:
            path = "Jev files it alone" + ("" if verdict == "duplicate" and d["duplicate_of"] in ids.split("|") else " (WRONG)")
        elif d["duplicate_of"]:
            path = "Jev unsure -> Claude decides"
        else:
            path = "not a duplicate -> Claude writes it up"
        key = f"{verdict:<9} | {path}"
        tally[key] = tally.get(key, 0) + 1
    for k, v in sorted(tally.items()):
        print(f"{v:4}  {k}")


def writer(cases, models):
    for model in models:
        right = graded = tin = tout = 0
        t0 = time.time()
        todo = [c for c in cases if c[1] in ("new", "not_an_idea")]
        print(f"\n=== {model} ===")
        for text, verdict, _ in todo:
            w = ai_review.claude_write(text, None, NEEDS_SHORT, model=model)
            if not w:
                print("FAILED:", text)
                continue
            tin += w["usage"]["input_tokens"]; tout += w["usage"]["output_tokens"]
            ok = w["verdict"] == verdict
            graded += 1; right += ok
            print(f"{'✓' if ok else '✗'} {text[:70]:<70} want {verdict:<12} got {w['verdict']} ({w['confidence']})")
            if w["verdict"] == "new" and w["draft"]:
                d = w["draft"]
                print(f"      “{d['hook']}” / {d['title']}\n      {d['summary']}\n"
                      f"      place: {d['place']} | result: {d['result']} | {d['setup_type']}, {d['difficulty']}, "
                      f"{d['phone_support']} | needs: {d['needs']}")
        n = len(todo)
        pi, po = PRICE.get(model, (0, 0))
        print(f"{model}: {right}/{graded} verdicts right | {(time.time() - t0) / n:.1f}s per idea | "
              f"${(tin * pi + tout * po) / 1e6 / n:.4f} per idea ({tin // n} in / {tout // n} out tokens)")


def claude(cases, ideas):
    right = graded = tin = tout = 0
    todo = [c for c in cases if c[1] in ("duplicate", "new")]
    for text, verdict, dup in todo:
        r = ai_review.claude_review(text, None, ideas, NEEDS_SHORT)
        if not r:
            print("FAILED:", text)
            continue
        tin += r["usage"]["input_tokens"]; tout += r["usage"]["output_tokens"]
        ok = r["verdict"] == verdict and (verdict != "duplicate" or r["duplicate_of"] == dup)
        graded += 1; right += ok
        print(f"{'✓' if ok else '✗'} {text[:72]:<72} want {verdict} {dup or ''}  got {r['verdict']} {r['duplicate_of'] or ''}")
    pi, po = PRICE.get(ai_review.MODEL, (0, 0))
    print(f"\n{ai_review.MODEL} (everything in one call): {right}/{graded} right | "
          f"${(tin * pi + tout * po) / 1e6 / len(todo):.4f} per idea")


NEEDS_SHORT = [{"id": n["id"], "label": n["label"]} for n in NEEDS]

if __name__ == "__main__":
    part, which = sys.argv[1], sys.argv[2]
    cases = {"dev": DEV, "holdout": HOLDOUT, "tune": TUNE, "test": TEST, "near": NEAR}[which]
    if part == "dupes":
        dupes(cases, bank())
    elif part == "writer":
        writer(cases, sys.argv[3].split(",") if len(sys.argv) > 3 else [ai_review.WRITER_MODEL])
    elif part == "route":
        route(cases, bank())
    elif part == "claude":
        claude(cases, bank())
