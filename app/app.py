"""NFC Idea Finder — web app (Flask).

Run locally:   python app/app.py            -> http://localhost:8000
On the Pi:     see README (Docker)."""
import hmac
import json
import os
import fcntl
import re
import sys
import threading
from datetime import datetime, timezone
from functools import wraps
from urllib.parse import quote, quote_plus

from flask import Flask, Response, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(__file__))
import ai_review                                  # noqa: E402
import database                                   # noqa: E402
import similar                                    # noqa: E402
from engines import ENGINES, available_engines   # noqa: E402
from questions import NEEDS, QUESTIONS, WORLDS     # noqa: E402
from tags import pick_tag                         # noqa: E402

app = Flask(__name__, static_folder="static", static_url_path="/static")

database.load_content()                  # JSON -> SQLite on every start
CATALOG, TAGS, IDEAS_BY_ID, WORLD_OF = {}, {}, {}, {}
VERSIONS = {}
SIMILAR = None


def reload_catalog():
    """(Re)read everything from SQLite. Called at start and whenever the bank changed."""
    global CATALOG, TAGS, IDEAS_BY_ID, WORLD_OF, VERSIONS, SIMILAR
    VERSIONS = database.versions()
    CATALOG = database.get_catalog()
    SIMILAR = similar.Index([i for i in CATALOG["ideas"] if i["status"] != "hidden"])
    TAGS = {t["id"]: t for t in CATALOG["tags"]}
    IDEAS_BY_ID = {i["id"]: i for i in CATALOG["ideas"]}
    need_world = {n["id"]: n["question"] for n in NEEDS}
    WORLD_OF = {}
    for n in NEEDS:
        for idea_id in n["ideas"]:
            WORLD_OF.setdefault(idea_id, set()).add(n["question"])
    for i in CATALOG["ideas"]:
        for need_id in i.get("needs") or []:
            if need_id in need_world:
                WORLD_OF.setdefault(i["id"], set()).add(need_world[need_id])


reload_catalog()


@app.before_request
def catalog_fresh():
    # The app runs as several processes; if another one changed the bank or the "I use this"
    # counts, catch up. One tiny query per API/page request (static files skip it).
    if request.path.startswith("/static/"):
        return
    now = database.versions()
    if now.get("catalog_version") != VERSIONS.get("catalog_version"):
        reload_catalog()
    elif now.get("uses_version") != VERSIONS.get("uses_version"):
        CATALOG["uses"] = database.get_uses()
        VERSIONS["uses_version"] = now.get("uses_version")


def similar_ideas(text, limit=5):
    """The "already in the bank?" hint: TF-IDF word matching (see similar.py). Free, local, instant."""
    return [{"id": i["id"], "title": i["hook"] or i["title"], "summary": i["summary"],
             "community": bool(i.get("community")), "score": round(s, 2)} for s, i in SIMILAR.search(text, limit)]


def safe_url(url):
    """Only plain web links. Visitor links end up clickable on the site, so no javascript: and friends."""
    url = (url or "").strip()
    return url if re.match(r"^https?://[^\s<>\"']+$", url, re.I) and len(url) <= 500 else None

MAIN_KINDS = {"diy", "business", "maker"}


# ------------------------------------------------------------------ helpers
def source_link(link):
    """Best link we have for a source: real URL (+ timestamp) or a search as fallback."""
    src = link["source"]
    if src["type"] == "editorial":          # written by the site's creator: nothing to link to
        return None, False
    if src["type"] == "community":          # shared on Tapwise: link only if they gave one
        return src["url"] or None, False
    if src["url"]:
        url = src["url"]
        if link["start_seconds"] and "youtu" in url:
            url += ("&" if "?" in url else "?") + f"t={link['start_seconds']}s"
        elif link.get("anchor_quote") and "youtu" not in url:
            # "#:~:text=" makes the browser scroll to and highlight this exact text (Chrome, Edge, Safari)
            snippet = link["anchor_quote"].split("...")[0].split("\u2026")[0].strip(" .,\"'\u201c\u201d")
            snippet = " ".join(snippet.split()[:8])
            if len(snippet) > 12:
                url += "#:~:text=" + quote(snippet, safe="")
        return url, False
    if src["type"] == "book":
        return "https://www.google.com/search?tbm=bks&q=" + quote_plus(src["title"]), True
    return "https://www.youtube.com/results?search_query=" + quote_plus(f"{src['title']} {src['creator_name']}"), True


SETUP_TIME = {"easy": "about 5 minutes", "medium": "about 20 minutes", "advanced": "an afternoon project"}


PLATFORM_DOMAIN = {"YouTube": "youtube.com", "TikTok": "tiktok.com", "Instagram": "instagram.com",
                   "Reddit": "reddit.com", "blog": None}


APPS = {
    "nfc_tools_ios": ("NFC Tools (App Store)", "https://apps.apple.com/app/nfc-tools/id1252962749"),
    "nfc_tools_android": ("NFC Tools (Google Play)", "https://play.google.com/store/apps/details?id=com.wakdev.wdnfc"),
    "nfc_tools_pro": ("NFC Tools Pro (Google Play)", "https://play.google.com/store/apps/details?id=com.wakdev.nfctools.pro"),
    "macrodroid": ("MacroDroid (Google Play)", "https://play.google.com/store/apps/details?id=com.arlosoft.macrodroid"),
    "shortcuts": ("Shortcuts (App Store)", "https://apps.apple.com/app/shortcuts/id915249334"),
    "ha_ios": ("Home Assistant (App Store)", "https://apps.apple.com/app/home-assistant/id1099568401"),
    "ha_android": ("Home Assistant (Google Play)", "https://play.google.com/store/apps/details?id=io.homeassistant.companion.android"),
}


def _apps(keys):
    return [{"label": APPS[k][0], "url": APPS[k][1]} for k in keys]


def shop_url(tag):
    return "https://www.google.com/search?tbm=shop&q=" + quote_plus(tag["search_term"]) if tag else None


def setup_steps(idea, tag, phone):
    """Four simple steps: get the tag, set it up on YOUR phone, stick it, tap. Each can carry links."""
    t, result = idea["setup_type"], idea["result"] or "your chosen action runs"
    ios, android = phone in ("iphone", "both", None), phone in ("android", "both", None)
    links = []
    if t == "link":
        how = "Open the free NFC Tools app \u2192 Write \u2192 add the link, wifi, contact or text \u2192 hold the tag to your phone."
        links = _apps((["nfc_tools_ios"] if ios else []) + (["nfc_tools_android"] if android else []))
    elif t == "smarthome":
        how = "In the Home Assistant app: Settings \u2192 Tags \u2192 Add tag, scan it, then make an automation for what should happen."
        links = _apps((["ha_ios"] if ios else []) + (["ha_android"] if android else []))
    elif t == "app":
        how = "Install an app that supports NFC tags for this (see the creators below) and scan the tag once inside the app."
    elif t == "maker":
        how = "Connect a PN532 reader to a Raspberry Pi or Arduino and run a small program that reacts to each card."
    elif phone == "iphone":
        how = "Open the Shortcuts app (already on your iPhone) \u2192 Automation \u2192 New \u2192 NFC \u2192 scan the tag, then choose what should happen."
        links = _apps(["shortcuts"])
    elif phone == "android":
        how = "Install NFC Tools Pro or MacroDroid, create a task (what should happen) and link it to the tag."
        links = _apps(["nfc_tools_pro", "macrodroid"])
    else:
        how = "iPhone: Shortcuts app \u2192 Automation \u2192 NFC. Android: NFC Tools Pro or MacroDroid. Scan the tag and choose what should happen."
        links = _apps(["shortcuts", "nfc_tools_pro", "macrodroid"])
    return [
        {"icon": "\U0001F3F7\uFE0F", "title": "Get the tag", "text": (tag["name"] + " \u00b7 " + tag["price_hint"]) if tag else "See the creators below",
         "links": [{"label": "See it in shops", "url": shop_url(tag)}] if tag else []},
        {"icon": "\U0001F4F1", "title": "Set it up", "text": how, "links": links},
        {"icon": "\U0001F4CD", "title": "Stick it", "text": (idea["place"] or "where you need it").capitalize(), "links": []},
        {"icon": "\u2728", "title": "Tap", "text": result[0].upper() + result[1:] + ".", "links": []},
    ]


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
        g = grouped.setdefault((src["id"], link.get("credit")), {
            "creator": ("u/" + link["credit"]) if link.get("credit")
            else ("a member of " + src["title"].rsplit(" : ", 1)[-1]) if src["platform"] == "Reddit"
            else src["creator_name"],
            "title": src["title"], "type": src["type"],
            "platform": src["platform"], "url": url, "is_search": is_search, "quotes": [],
            "domain": PLATFORM_DOMAIN.get(src["platform"]),
            "start_seconds": link["start_seconds"]})
        if link["anchor_quote"]:
            g["quotes"].append(link["anchor_quote"])
    return {
        "id": idea["id"], "title": idea["title"], "hook": idea["hook"], "kind": idea["kind"], "summary": idea["summary"],
        "steps": setup_steps(idea, tag, answers.get("phone")) if idea["kind"] in MAIN_KINDS else [],
        "how_it_works": idea["how_it_works"], "setup": idea["setup_by_platform"],
        "difficulty": idea["difficulty"], "setup_time": SETUP_TIME.get(idea["difficulty"]),
        "cost_level": idea["cost_level"], "phone_support": idea["phone_support"],
        "business": {"model": idea["business_model"], "who_pays": idea["who_pays"],
                     "startup_cost": idea["startup_cost_level"]} if idea["business_model"] else None,
        "needs_review": idea["status"] == "needs_review", "review_flags": idea["review_flags"],
        "score": round(score, 1), "why": why, "warnings": warnings,
        "tag": {"id": tag["id"], "name": tag["name"], "search_term": tag["search_term"], "shop_url": shop_url(tag),
                "price_hint": tag["price_hint"], "why": tag_why} if tag else None,
        "sources": list(grouped.values()),
        "uses": CATALOG["uses"].get(idea["id"], 0),
        "community": bool(idea.get("community")),
        "contributor": idea["sources"][0]["source"]["creator_name"] if idea.get("community") else None,
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
    visible = [i for i in CATALOG["ideas"] if i["status"] != "hidden" and i["kind"] in MAIN_KINDS]
    creators = {s["creator_name"] for s in CATALOG["sources"].values() if s["creator_name"]}
    community = [i for i in visible if i.get("community")]
    creators |= {i["sources"][0]["source"]["creator_name"] for i in community}
    return jsonify(questions=QUESTIONS, engines=available_engines(),
                   worlds=[{"key": k, "label": t} for k, t, _, _ in WORLDS],
                   stats={"ideas": len(visible), "creators": len(creators), "sources": len(CATALOG["sources"]),
                          "community": len(community), "uses": sum(CATALOG["uses"].values())})


# hand-picked, so people who "don't know what NFC is for" see the best examples first
EXPLORE = [
    ("home", "\U0001F3E0 Home", ["i006", "i010", "i003", "i043"]),
    ("car", "\U0001F697 Car", ["i040", "i041", "i042", "i006"]),
    ("desk", "\U0001F4BB Desk & study", ["i031", "i033", "i032", "i044"]),
    ("health", "\U0001F4AA Health & habits", ["i028", "i027", "i030", "i024"]),
    ("business", "\u2615 Business", ["i049", "i050", "i043", "i052"]),
]


@app.get("/api/explore")
def explore():
    """A few great ideas per place, for people who want to browse before answering."""
    out = []
    for key, label, ids in EXPLORE:
        ideas = [IDEAS_BY_ID[x] for x in ids if x in IDEAS_BY_ID and IDEAS_BY_ID[x]["status"] != "hidden"]
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
    if (d.get("source_url") or "").strip() and not safe_url(d.get("source_url")):
        return jsonify(error="The link should start with http:// or https://"), 400
    if database.recent_duplicate_submission(desc[:2000]):   # same text again within minutes = a double click
        return jsonify(ok=True)
    clean = lambda k, n: ((d.get(k) or "").strip()[:n] or None) if isinstance(d.get(k), (str, type(None))) else None
    context = d.get("context") if isinstance(d.get("context"), dict) else None
    database.add_submission({
        "description": desc[:2000], "place": clean("place", 200), "source_url": safe_url(d.get("source_url")),
        "submitter_name": clean("submitter_name", 80), "email": clean("email", 200),
        "credit_ok": bool(d.get("credit_ok") and clean("submitter_name", 80)),
        "context": context if context and len(json.dumps(context)) <= 4000 else None})
    start_ai_sweep()                                         # in the background: the visitor doesn't wait
    return jsonify(ok=True)


# ------------------------------------------------------------------ AI review (fully automatic)
# Every suggestion is reviewed by the AI (Jev, then Claude if needed; see ai_review.py) and the verdict is final:
#   new -> straight into the bank (from the AI's cleaned-up draft), credited to the visitor
#   duplicate -> filed as a duplicate of the existing idea;  not_an_idea -> rejected
# Nobody has to review anything. /admin shows every decision with an undo button.
# Without an API key (or when the AI fails / the daily limit is hit) ideas simply wait as "pending".
AI_DAILY_LIMIT = int(os.environ.get("TAPWISE_AI_DAILY_LIMIT", 50))   # caps the bill if someone floods the form
AI_LOCK = database.DB_PATH.parent / "ai-review.lock"


def run_ai_review(sub_id):
    sub = database.get_submission(sub_id)
    if not sub:
        return None
    ideas = [{"id": i["id"], "title": i["title"], "summary": i["summary"], "place": i.get("place"),
              "result": i.get("result")} for i in CATALOG["ideas"] if i["status"] != "hidden"]
    # (only the idea text goes to the AI services, never names or emails)
    needs = [{"id": n["id"], "label": n["label"]} for n in NEEDS]
    r = ai_review.review(sub["description"], sub.get("place"), ideas, needs)
    if not r:
        return None
    r["reviewed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if sub["status"] == "pending":
        if r["verdict"] == "duplicate":
            database.set_submission_status(sub_id, "duplicate", r["duplicate_of"])
            r["auto"] = "duplicate"
        elif r["verdict"] == "not_an_idea":
            database.set_submission_status(sub_id, "rejected")
            r["auto"] = "rejected"
        elif r["draft"]:
            database.add_community_idea(sub_id, {
                **r["draft"], "contributor": sub["submitter_name"] if sub["credit_ok"] else None,
                "source_url": safe_url(sub["source_url"])})
            reload_catalog()
            r["auto"] = "approved"
    database.set_ai_review(sub_id, r)
    return r


def ai_sweep():
    """Review every pending idea that has no AI review yet. One sweep at a time across all processes."""
    database.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AI_LOCK, "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return                                          # another process is already on it
        tried = set()
        while database.ai_reviews_today() < AI_DAILY_LIMIT:
            todo = [i for i in database.pending_without_ai_review() if i not in tried]
            if not todo:
                break
            tried.add(todo[0])
            run_ai_review(todo[0])


def start_ai_sweep():
    if ai_review.enabled():
        threading.Thread(target=ai_sweep, daemon=True).start()


start_ai_sweep()            # catch up on anything sent while the AI was off or failing


@app.get("/api/ideas/similar")
def similar():
    """Used by the "Add an idea" form (heads-up) and the admin page (duplicate check)."""
    return jsonify(matches=similar_ideas(request.args.get("q") or ""))


@app.get("/api/ideas")
def browse():
    """The bank: every idea, searchable, filterable by world, sorted by most used or newest."""
    q = (request.args.get("q") or "").lower().strip()
    world = request.args.get("world") or ""
    sort = request.args.get("sort") or "popular"
    phone = request.args.get("phone")
    out = []
    for i in CATALOG["ideas"]:
        if i["status"] == "hidden" or i["kind"] not in MAIN_KINDS:
            continue
        if world == "community" and not i.get("community"):
            continue
        if world and world != "community" and world not in WORLD_OF.get(i["id"], set()):
            continue
        if q and q not in " ".join(filter(None, [i["title"], i["hook"], i["summary"], i["place"], i["result"]])).lower():
            continue
        out.append(i)
    if sort == "new":
        out.sort(key=lambda i: (i.get("approved_at") or "", i["id"]), reverse=True)
    else:
        out.sort(key=lambda i: (-CATALOG["uses"].get(i["id"], 0), not i.get("community"), i["id"]))
    return jsonify(total=len(out), ideas=[present(i, 0, [], [], {"phone": phone}) for i in out[:200]])


@app.post("/api/ideas/<idea_id>/use")
def use_idea(idea_id):
    """Someone says "I use this": the idea climbs in the bank and the creator sees it helped."""
    if idea_id not in IDEAS_BY_ID:
        return jsonify(error="unknown idea"), 404
    n = database.add_use(idea_id)
    CATALOG["uses"][idea_id] = n
    VERSIONS["uses_version"] = database.versions().get("uses_version")
    return jsonify(uses=n)


# ------------------------------------------------------------------ admin (only you)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def admin_only(f):
    """Browser asks for a password. No ADMIN_PASSWORD set = admin is switched off."""
    @wraps(f)
    def wrapper(*a, **kw):
        auth = request.authorization
        if not ADMIN_PASSWORD:
            return jsonify(error="Admin is off. Start the app with ADMIN_PASSWORD=..."), 403
        if not auth or not hmac.compare_digest(auth.password or "", ADMIN_PASSWORD):
            return Response("Login needed", 401, {"WWW-Authenticate": 'Basic realm="Tapwise admin"'})
        return f(*a, **kw)
    return wrapper


@app.get("/admin")
@admin_only
def admin_page():
    return send_from_directory(app.static_folder, "admin.html")


@app.get("/api/suggestions")
@app.get("/api/admin/submissions")
@admin_only
def suggestions():
    return jsonify(submissions=database.list_submissions(), ai_enabled=ai_review.enabled(),
                   titles={i["id"]: i["title"] for i in CATALOG["ideas"]},
                   needs=[{"id": n["id"], "label": n.get("short") or n["label"], "world": n["question"]} for n in NEEDS],
                   worlds=[{"key": k, "label": t} for k, t, _, _ in WORLDS])


@app.post("/api/admin/submissions/<int:sub_id>/approve")
@admin_only
def approve(sub_id):
    sub = database.get_submission(sub_id)
    if not sub:
        return jsonify(error="not found"), 404
    f = request.get_json(force=True) or {}
    if not (f.get("title") and f.get("summary")):
        return jsonify(error="Title and summary are needed."), 400
    if "contributor" not in f:
        f["contributor"] = sub["submitter_name"] if sub["credit_ok"] else None
    f["source_url"] = safe_url(f.get("source_url", sub["source_url"]))
    cid = database.add_community_idea(sub_id, f)
    reload_catalog()
    return jsonify(ok=True, id=cid)


@app.post("/api/admin/submissions/<int:sub_id>/ai-review")
@admin_only
def ai_review_now(sub_id):
    """Admin button: (re)run the AI review, e.g. for ideas sent before the AI was switched on."""
    if not ai_review.enabled():
        return jsonify(error="AI is off. Start the app with ANTHROPIC_API_KEY=..."), 400
    r = run_ai_review(sub_id)
    return jsonify(ok=bool(r), review=r) if r else (jsonify(error="The AI didn't answer, try again later."), 502)


@app.post("/api/admin/submissions/<int:sub_id>/unpublish")
@admin_only
def unpublish(sub_id):
    """Undo for an idea the AI approved: take it out of the bank again."""
    if not database.remove_community_idea(sub_id):
        return jsonify(error="That idea isn't in the bank."), 400
    reload_catalog()
    return jsonify(ok=True)


@app.post("/api/admin/submissions/<int:sub_id>/status")
@admin_only
def set_status(sub_id):
    d = request.get_json(force=True) or {}
    status = d.get("status")
    if status not in ("pending", "rejected", "duplicate"):
        return jsonify(error="bad status"), 400
    database.set_submission_status(sub_id, status, d.get("linked_idea_id"))
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=bool(os.environ.get("DEBUG")))
