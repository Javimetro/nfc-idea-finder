"""NFC Idea Finder — web app (Flask).

Run locally:   python app/app.py            -> http://localhost:8000
On the Pi:     see README (Docker)."""
import os
import sys
from urllib.parse import quote_plus

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(__file__))
import database                                   # noqa: E402
from engines import ENGINES, available_engines   # noqa: E402
from questions import QUESTIONS                   # noqa: E402
from tags import pick_tag                         # noqa: E402

app = Flask(__name__, static_folder="static", static_url_path="/static")

database.load_content()                  # JSON -> SQLite on every start
CATALOG = database.get_catalog()
TAGS = {t["id"]: t for t in CATALOG["tags"]}

MAIN_KINDS = {"diy", "business", "maker"}


# ------------------------------------------------------------------ helpers
def source_link(link):
    """Best link we have for a source: real URL (+ timestamp) or a search as fallback."""
    src = link["source"]
    if src["url"]:
        url = src["url"]
        if link["start_seconds"] and "youtu" in url:
            url += ("&" if "?" in url else "?") + f"t={link['start_seconds']}s"
        return url, False
    if src["type"] == "book":
        return "https://www.google.com/search?tbm=bks&q=" + quote_plus(src["title"]), True
    return "https://www.youtube.com/results?search_query=" + quote_plus(f"{src['title']} {src['creator_name']}"), True


SETUP_TIME = {"easy": "about 5 minutes", "medium": "about 20 minutes", "advanced": "an afternoon project"}


def present(idea, score, why, warnings, answers):
    facts = set(answers.get("about") or [])
    # strangers tap business tags -> recommend a tougher tag
    cond = {"public"} if facts & {"business_owner", "money"} and idea["kind"] == "business" else set()
    tag, tag_why = pick_tag(idea, {"conditions": list(cond)}, TAGS) if idea["kind"] in MAIN_KINDS else (None, [])
    # one entry per source (a video can explain the same idea at several moments)
    grouped = {}
    for link in idea["sources"]:
        url, is_search = source_link(link)
        src = link["source"]
        g = grouped.setdefault(src["id"], {
            "creator": src["creator_name"], "title": src["title"], "type": src["type"],
            "platform": src["platform"], "url": url, "is_search": is_search, "quotes": [],
            "start_seconds": link["start_seconds"]})
        if link["anchor_quote"]:
            g["quotes"].append(link["anchor_quote"])
    return {
        "id": idea["id"], "title": idea["title"], "kind": idea["kind"], "summary": idea["summary"],
        "how_it_works": idea["how_it_works"], "setup": idea["setup_by_platform"],
        "difficulty": idea["difficulty"], "setup_time": SETUP_TIME.get(idea["difficulty"]),
        "cost_level": idea["cost_level"], "phone_support": idea["phone_support"],
        "business": {"model": idea["business_model"], "who_pays": idea["who_pays"],
                     "startup_cost": idea["startup_cost_level"]} if idea["business_model"] else None,
        "needs_review": idea["status"] == "needs_review", "review_flags": idea["review_flags"],
        "score": round(score, 1), "why": why, "warnings": warnings,
        "tag": {"id": tag["id"], "name": tag["name"], "search_term": tag["search_term"],
                "price_hint": tag["price_hint"], "why": tag_why} if tag else None,
        "sources": list(grouped.values()),
    }


def tips_for(answers, results):
    tips = []
    facts = set(answers.get("about") or [])
    if facts & {"business_owner", "money"}:
        tips.append("Lock tags that customers will tap (NFC Tools \u2192 Other \u2192 Lock tag), so nobody can overwrite them. Point them to a link you control, so you can change where they go without touching the tag.")
    if answers.get("phone") in ("iphone", "both"):
        tips.append("iPhone: a tag with a link opens by itself. For anything else (timers, messages, lights) use the Shortcuts app \u2192 Automation \u2192 NFC, and scan the tag once to register it.")
    if answers.get("phone") in ("android", "both"):
        tips.append("Android: write tags with the free NFC Tools app. For timers, messages or lights, NFC Tools Pro, MacroDroid or Tasker react when you tap a tag.")
    if any(r["tag"] and r["tag"]["id"] == "t_antimetal" for r in results):
        tips.append("Normal tags stop working on metal (fridges, washing machines, cars). Buy tags labelled \u2018anti-metal\u2019.")
    tips.append("Start with ONE idea. Most people keep the tags they use every day and forget the rest, so pick the one that solves your most annoying moment.")
    return tips


# ------------------------------------------------------------------ routes
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/meta")
def meta():
    visible = [i for i in CATALOG["ideas"] if i["status"] != "hidden"]
    creators = {s["creator_name"] for s in CATALOG["sources"].values() if s["creator_name"]}
    return jsonify(questions=QUESTIONS, engines=available_engines(),
                   stats={"ideas": len(visible), "creators": len(creators), "sources": len(CATALOG["sources"])})


# hand-picked, so people who "don't know what NFC is for" see the best examples first
EXPLORE = [
    ("home", "\U0001F3E0 Home", ["i006", "i010", "i003", "i043"]),
    ("car", "\U0001F697 Car", ["i040", "i041", "i042", "i006"]),
    ("desk", "\U0001F4BB Desk & study", ["i031", "i033", "i032", "i044"]),
    ("health", "\U0001F4AA Health & habits", ["i028", "i027", "i030", "i024"]),
    ("business", "\u2615 Business", ["i049", "i050", "i043", "i052"]),
]
IDEAS_BY_ID = {i["id"]: i for i in CATALOG["ideas"]}


@app.get("/api/explore")
def explore():
    """A few great ideas per place, for people who want to browse before answering."""
    out = []
    for key, label, ids in EXPLORE:
        ideas = [IDEAS_BY_ID[x] for x in ids if IDEAS_BY_ID[x]["status"] != "hidden"]
        out.append({"key": key, "label": label,
                    "ideas": [{"title": i["title"], "summary": i["summary"],
                               "setup_time": SETUP_TIME.get(i["difficulty"]),
                               "creators": len({l["source_id"] for l in i["sources"]})} for i in ideas]})
    return jsonify(out)


@app.post("/api/match")
def match():
    body = request.get_json(force=True) or {}
    answers = body.get("answers") or {}
    engine = ENGINES.get(body.get("engine") or "rules", ENGINES["rules"])
    try:
        ranked = engine.rank(CATALOG, answers)
    except NotImplementedError as e:
        return jsonify(error=str(e)), 501

    usable = [(s, i, y, w) for s, i, y, w in ranked if i["kind"] in MAIN_KINDS]
    matched = [present(i, s, y, w, answers) for s, i, y, w in usable if y][:8]
    # nothing ticked? fall back to what fits their life
    also = [present(i, s, y, w, answers) for s, i, y, w in usable if not y and s > 0][:4 if matched else 8]

    shopping = {}
    for idea in matched or also:
        if idea["tag"]:
            item = shopping.setdefault(idea["tag"]["id"], {**idea["tag"], "ideas": []})
            item["ideas"].append(idea["title"])
    return jsonify(engine=engine.NAME, engine_label=engine.LABEL, results=matched, also=also,
                   shopping_list=sorted(shopping.values(), key=lambda x: -len(x["ideas"])),
                   tips=tips_for(answers, matched or also))


@app.post("/api/suggest")
def suggest():
    d = request.get_json(force=True) or {}
    if d.get("website"):                        # honeypot field: humans never fill it
        return jsonify(ok=True)
    desc = (d.get("description") or "").strip()
    if len(desc) < 10:
        return jsonify(error="Please describe the idea in a sentence or two."), 400
    database.add_submission({**d, "description": desc[:2000]})
    return jsonify(ok=True)


@app.get("/api/suggestions")
def suggestions():
    return jsonify(database.list_submissions())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=bool(os.environ.get("DEBUG")))
