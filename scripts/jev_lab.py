"""Jev lab: record Jev's raw answers for the test ideas once, then try duplicate rules on them offline.

    collect TUNE|TEST   ask Jev everything once, save to scripts/lab_results/<set>.json (no decisions)
    analyse TUNE|TEST   score many decision rules on the saved answers (no API calls)

Run in the container so it has the TypeSafe key and the idea bank (Claude is never called here):
    docker run --rm --env-file ~/tapwise.env -e ANTHROPIC_API_KEY= -v $PWD/scripts:/srv/scripts \
        tapwise-test python /srv/scripts/jev_lab.py collect TUNE
"""
import concurrent.futures as cf
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "app"))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "lab_results")

SHORTLIST_Q = {
    # A: what production used in step 27
    "A": ("Which existing idea is the same idea as the visitor_suggestion: the tag is used in the same situation and "
          "the user gets the same result, even if it's worded differently? Choose none if no existing idea is the same idea.",
          "plain"),
    # B: same question, richer option text (where the tag goes, what happens)
    "B": ("Which existing idea is the same idea as the visitor_suggestion: the tag is used in the same situation and "
          "the user gets the same result, even if it's worded differently? Choose none if no existing idea is the same idea.",
          "rich"),
    # C: "already covers" wording, rich options
    "C": ("Which existing idea already covers the visitor_suggestion, so adding the suggestion to the idea bank would "
          "repeat it? Choose none if the suggestion would add something genuinely new.", "rich"),
}
PAIR_Q = {
    "same_idea": "The new_idea is the same NFC idea as the existing_idea, just worded differently",
    "same_problem": "The new_idea and the existing_idea solve the same everyday problem",
    "same_result": "When the tag is tapped, the new_idea and the existing_idea give the user the same result",
    "same_place": "In the new_idea and the existing_idea, the tag is used in the same kind of place or situation",
    "nothing_new": "Someone who already knows the existing_idea would learn nothing new from the new_idea",
    "covers": "The existing_idea already covers the new_idea, even if the new_idea is one specific example of it",
}
SIM_LEVELS = ["Unrelated ideas", "Same general area, but a different idea",
              "Similar, but with a clearly different purpose or result",
              "Mostly the same idea, with a small twist", "The same idea, just worded differently"]
TOP = 5     # candidates per shortlist variant that get a side-by-side check


def option_text(i, style):
    t = f"{i['title']}. {i['summary']}"
    if style == "rich" and i.get("place"):
        t += f" (Tag goes: {i['place']}. When tapped: {i['result']}.)"
    return t


def collect(name):
    import ai_review
    import database
    import review_cases_big as rc
    database.load_content()
    ideas = [i for i in database.get_catalog()["ideas"] if i["status"] != "hidden"]
    by_id = {i["id"]: i for i in ideas}

    def one(case):
        text, expected, ids, style = case
        rec = {"text": text, "expected": expected, "ids": ids, "style": style, "short": {}, "pairs": {}, "tokens": 0}
        for key, (instr, ostyle) in SHORTLIST_Q.items():
            out = ai_review._jev({"visitor_suggestion": text}, {"q": {
                "type": "choice", "instructions": instr,
                "criteria": {**{i["id"]: option_text(i, ostyle) for i in ideas}, "none": "None of these"}}})
            p = out["answers"]["q"]["probabilities"]
            rec["short"][key] = dict(sorted(p.items(), key=lambda x: -x[1])[:15]) | {"none": p.get("none", 0)}
            rec["tokens"] += out["usage"]["input_tokens"]
        cands = {c for s in rec["short"].values() for c in [k for k in s if k != "none"][:TOP]}
        for c in cands:
            i = by_id[c]
            existing = {"title": i["title"], "summary": i["summary"]}
            if i.get("place"):
                existing |= {"where_the_tag_goes": i["place"], "what_happens_when_tapped": i["result"]}
            qs = {k: {"type": "noul", "instructions": v} for k, v in PAIR_Q.items()}
            qs["similarity"] = {"type": "score", "criteria": SIM_LEVELS,
                                "instructions": "How similar is the new_idea to the existing_idea?"}
            out = ai_review._jev({"new_idea": text, "existing_idea": existing}, qs)
            a = out["answers"]
            rec["pairs"][c] = {k: round(a[k]["noul"], 4) for k in PAIR_Q} | {
                "similarity": round(a["similarity"]["score"], 3),
                "similarity_p": {k: round(v, 4) for k, v in a["similarity"]["probabilities"].items()}}
            rec["tokens"] += out["usage"]["input_tokens"]
        return rec

    cases = getattr(rc, name)
    with cf.ThreadPoolExecutor(8) as ex:
        recs = list(ex.map(one, cases))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{name}.json"), "w") as f:
        json.dump(recs, f, indent=1)
    print(f"{name}: {len(recs)} ideas, {sum(r['tokens'] for r in recs)} Jev tokens "
          f"(${sum(r['tokens'] for r in recs) / 1e6 * 0.042:.4f})")


# ------------------------------------------------------------------ offline analysis
def decide(rec, rule):
    """Apply one rule to the saved answers. Returns a bank id or None (= new)."""
    s = rec["short"][rule["short"]] if rule["short"] != "AC" else {
        k: (rec["short"]["A"].get(k, 0) + rec["short"]["C"].get(k, 0)) / 2
        for k in set(rec["short"]["A"]) | set(rec["short"]["C"])}
    cands = [(k, p) for k, p in sorted(s.items(), key=lambda x: -x[1]) if k != "none"][:rule["k"]]
    best, best_val = None, -1
    for cid, pick in cands:
        pr = rec["pairs"].get(cid)
        if pr is None:
            continue
        feats = [pr[f] for f in rule["feats"]] if rule["feats"] != ["sim"] else [pr["similarity"] / 4]
        agree = min(feats) if rule["combine"] == "min" else sum(feats) / len(feats)
        ok = (pick >= rule["pick"] and agree >= rule["agree"]) or agree >= rule["strong"]
        if ok and agree + pick / 10 > best_val:
            best, best_val = cid, agree + pick / 10
    return best


def score(recs, rule):
    r = {"right": 0, "n": 0, "false_dup": 0, "missed": 0, "wrong_id": 0}
    for rec in recs:
        if rec["expected"] == "?":
            continue
        got = decide(rec, rule)
        r["n"] += 1
        if rec["expected"] == "duplicate":
            ok_ids = rec["ids"].split("|")
            if got in ok_ids:
                r["right"] += 1
            elif got is None:
                r["missed"] += 1
            else:
                r["wrong_id"] += 1
        else:
            if got is None:
                r["right"] += 1
            else:
                r["false_dup"] += 1
    return r


CURRENT = {"short": "A", "k": 3, "feats": ["same_idea", "same_problem"], "combine": "min",
           "pick": 0.5, "agree": 0.5, "strong": 0.8}


def analyse(name):
    recs = json.load(open(os.path.join(OUT, f"{name}.json")))
    base = score(recs, CURRENT)
    print(f"{name}: current production rule -> {base}")
    feat_sets = [["same_idea", "same_problem"], ["same_idea"], ["covers"], ["nothing_new"], ["sim"],
                 ["same_idea", "covers"], ["covers", "same_problem"], ["same_problem", "same_result"],
                 ["same_idea", "same_problem", "covers"], ["covers", "same_result"], ["same_result", "same_place"]]
    results = []
    for short, k, feats, combine, pick, agree, strong in itertools.product(
            ["A", "B", "C", "AC"], [1, 3, 5], feat_sets, ["min", "mean"],
            [0.3, 0.5, 0.7], [0.3, 0.4, 0.5, 0.6], [0.7, 0.8, 0.9, 1.01]):
        if len(feats) == 1 and combine == "mean":
            continue
        rule = {"short": short, "k": k, "feats": feats, "combine": combine, "pick": pick, "agree": agree, "strong": strong}
        r = score(recs, rule)
        # rank: most right, then fewest false duplicates (they throw away good ideas)
        results.append((r["right"] - 0.5 * r["false_dup"], r, rule))
    results.sort(key=lambda x: -x[0])
    for _, r, rule in results[:25]:
        print(r, rule)
    return results


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    collect(name) if cmd == "collect" else analyse(name)
