"""SQLite database for the NFC Idea Finder.

The curated content (sources, ideas, links, tag profiles) lives as JSON files in /db
and is (re)loaded into SQLite every time the app starts. That way you edit JSON,
restart, and the site is up to date.

Visitor suggestions live only in SQLite and are never overwritten.
"""
import fcntl
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "db"
DB_PATH = ROOT / "app" / "data" / "nfc.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY, title TEXT, url TEXT, type TEXT, platform TEXT,
    creator_name TEXT, creator_url TEXT, language TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY, title TEXT, kind TEXT, status TEXT, summary TEXT,
    how_it_works TEXT, setup_by_platform TEXT, phone_support TEXT,
    difficulty TEXT, cost_level TEXT,
    audience TEXT, settings TEXT, goals TEXT,        -- JSON arrays
    tag_needs TEXT, review_flags TEXT,              -- JSON
    business_model TEXT, who_pays TEXT, startup_cost_level TEXT,
    hook TEXT, place TEXT, result TEXT, setup_type TEXT
);
CREATE TABLE IF NOT EXISTS idea_sources (
    idea_id TEXT, source_id TEXT, start_seconds INTEGER, end_seconds INTEGER, anchor_quote TEXT, credit TEXT
);
CREATE TABLE IF NOT EXISTS tag_profiles (
    id TEXT PRIMARY KEY, data TEXT                  -- whole profile as JSON
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL, source_url TEXT, start_seconds INTEGER,
    submitter_name TEXT, credit_ok INTEGER DEFAULT 0, email TEXT,
    context TEXT,                                   -- quiz answers, if sent from the results page
    status TEXT DEFAULT 'pending', linked_idea_id TEXT,
    submitted_at TEXT DEFAULT (datetime('now'))
);
-- ideas shared by visitors and approved by the admin (never overwritten by the JSON reload)
CREATE TABLE IF NOT EXISTS community_ideas (
    id TEXT PRIMARY KEY,                             -- "c001", "c002"...
    submission_id INTEGER,
    title TEXT, hook TEXT, summary TEXT, how_it_works TEXT, place TEXT, result TEXT,
    setup_type TEXT, setup_by_platform TEXT, phone_support TEXT DEFAULT 'any', difficulty TEXT DEFAULT 'easy',
    settings TEXT, goals TEXT, needs TEXT,            -- JSON arrays
    contributor TEXT, source_url TEXT,
    original_text TEXT,                              -- the visitor's own words, only if they chose to publish them
    approved_at TEXT DEFAULT (datetime('now'))
);
-- "I use this" counter per idea is idea_uses, below
-- small counters that tell every worker process to refresh its copy: catalog_version (an idea was
-- added or removed), uses_version (someone tapped "I use this")
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value INTEGER);
CREATE TABLE IF NOT EXISTS idea_uses (
    idea_id TEXT PRIMARY KEY, uses INTEGER DEFAULT 0
);
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


CURATED = ("sources", "ideas", "idea_sources", "tag_profiles")


def _statements():
    """SCHEMA as separate statements (comments removed), so they can run inside one transaction."""
    lines = [l.split("--")[0] for l in SCHEMA.splitlines()]
    return [st.strip() for st in "\n".join(lines).split(";") if st.strip()]


def load_content():
    """Put the curated JSON files into SQLite (visitor submissions and community ideas untouched).

    The web server starts several processes at once, so this is careful:
    - one process at a time (file lock), and the whole rebuild is ONE transaction, so another
      process reading the bank sees the old tables or the new ones, never missing tables;
    - if the JSON files (and the schema) haven't changed since the last load, nothing is rebuilt."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH.parent / "load.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _load_content()


def _load_content():
    raw = {name: (JSON_DIR / f"{name}.json").read_text(encoding="utf-8") for name in CURATED}
    digest = int(hashlib.sha256((SCHEMA + "".join(raw.values())).encode()).hexdigest()[:12], 16)
    con = connect()
    con.isolation_level = None                      # we manage the transaction ourselves
    try:
        con.execute("BEGIN IMMEDIATE")
        for st in _statements():                    # CREATE TABLE IF NOT EXISTS ...
            con.execute(st)
        for table, col in (("submissions", "place TEXT"), ("submissions", "ai_review TEXT"),
                           ("submissions", "show_original INTEGER DEFAULT 0"),
                           ("community_ideas", "original_text TEXT")):   # older databases: add the newer columns
            try:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass
        same = con.execute("SELECT value FROM meta WHERE key = 'content_hash'").fetchone()
        if same and same[0] == digest:
            con.execute("COMMIT")
            return
        # curated tables are rebuilt from scratch (so new columns just work)
        for table in CURATED:
            con.execute(f"DROP TABLE IF EXISTS {table}")
        for st in _statements():
            con.execute(st)
        load = lambda name: json.loads(raw[name])
        con.executemany(
            "INSERT INTO sources VALUES (:id,:title,:url,:type,:platform,:creator_name,:creator_url,:language,:notes)",
            load("sources"))
        for i in load("ideas"):
            row = {**i}
            for k in ("audience", "settings", "goals", "tag_needs", "review_flags"):
                row[k] = json.dumps(i.get(k))
            con.execute(
                "INSERT INTO ideas VALUES (:id,:title,:kind,:status,:summary,:how_it_works,:setup_by_platform,"
                ":phone_support,:difficulty,:cost_level,:audience,:settings,:goals,:tag_needs,:review_flags,"
                ":business_model,:who_pays,:startup_cost_level,:hook,:place,:result,:setup_type)", row)
        con.executemany(
            "INSERT INTO idea_sources VALUES (:idea_id,:source_id,:start_seconds,:end_seconds,:anchor_quote,:credit)",
            load("idea_sources"))
        con.executemany("INSERT INTO tag_profiles VALUES (?, ?)",
                        [(t["id"], json.dumps(t)) for t in load("tag_profiles")])
        con.execute("INSERT INTO meta (key, value) VALUES ('content_hash', ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (digest,))
        _bump_catalog_version(con)                  # tell running processes to reload
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def get_catalog():
    """Everything the matching engines need, as plain Python objects (loaded once at startup)."""
    con = connect()
    sources = {r["id"]: dict(r) for r in con.execute("SELECT * FROM sources")}
    ideas = []
    for r in con.execute("SELECT * FROM ideas"):
        i = dict(r)
        for k in ("audience", "settings", "goals", "tag_needs", "review_flags"):
            i[k] = json.loads(i[k]) if i[k] else None
        i["sources"] = []
        ideas.append(i)
    by_id = {i["id"]: i for i in ideas}
    for r in con.execute("SELECT * FROM idea_sources"):
        link = dict(r)
        link["source"] = sources[link["source_id"]]
        by_id[link["idea_id"]]["sources"].append(link)
    tags = [json.loads(r["data"]) for r in con.execute("SELECT data FROM tag_profiles")]

    # community ideas look exactly like curated ones to the rest of the app
    for r in con.execute("SELECT * FROM community_ideas ORDER BY approved_at"):
        c = dict(r)
        src = {"id": "community:" + c["id"], "title": "Shared on Tapwise", "url": c["source_url"], "type": "community",
               "platform": None, "creator_name": c["contributor"] or "A Tapwise visitor", "creator_url": None,
               "language": "en", "notes": None}
        ideas.append({
            "id": c["id"], "title": c["title"], "kind": "diy", "status": "ok", "summary": c["summary"],
            "how_it_works": c["how_it_works"], "setup_by_platform": c["setup_by_platform"],
            "phone_support": c["phone_support"] or "any", "difficulty": c["difficulty"] or "easy", "cost_level": "under_5_eur",
            "audience": ["personal"], "settings": json.loads(c["settings"] or "[]"), "goals": json.loads(c["goals"] or "[]"),
            "tag_needs": {"form": "sticker", "on_metal": False, "waterproof": False, "rewritable": True, "secure": False, "memory": "small"},
            "review_flags": [], "business_model": None, "who_pays": None, "startup_cost_level": None,
            "hook": c["hook"] or c["title"], "place": c["place"], "result": c["result"], "setup_type": c["setup_type"] or "automation",
            "needs": json.loads(c["needs"] or "[]"), "community": True, "approved_at": c["approved_at"],
            "original_text": c.get("original_text"),
            "sources": [{"idea_id": c["id"], "source_id": src["id"], "start_seconds": None, "end_seconds": None,
                         "anchor_quote": None, "credit": None, "source": src}],
        })
    uses = {r["idea_id"]: r["uses"] for r in con.execute("SELECT * FROM idea_uses")}
    con.close()
    return {"ideas": ideas, "sources": sources, "tags": tags, "uses": uses}


def add_submission(d):
    con = connect()
    cur = con.execute(
        "INSERT INTO submissions (description, place, source_url, start_seconds, submitter_name, credit_ok, email, context,"
        " show_original) VALUES (?,?,?,?,?,?,?,?,?)",
        (d["description"], d.get("place"), d.get("source_url"), d.get("start_seconds"), d.get("submitter_name"),
         1 if d.get("credit_ok") else 0, d.get("email"), json.dumps(d.get("context")) if d.get("context") else None,
         1 if d.get("show_original") else 0))
    sub_id = cur.lastrowid
    con.commit()
    con.close()
    return sub_id


def recent_duplicate_submission(description, minutes=10):
    con = connect()
    hit = con.execute("SELECT 1 FROM submissions WHERE description = ? AND submitted_at >= datetime('now', ?)",
                      (description, f"-{minutes} minutes")).fetchone()
    con.close()
    return bool(hit)


def list_submissions():
    con = connect()
    rows = [dict(r) for r in con.execute("SELECT * FROM submissions ORDER BY submitted_at DESC")]
    con.close()
    for r in rows:
        r["ai_review"] = json.loads(r["ai_review"]) if r.get("ai_review") else None
    return rows


def ai_reviews_today():
    con = connect()
    n = con.execute("SELECT COUNT(*) FROM submissions WHERE json_extract(ai_review, '$.reviewed_at')"
                    " >= datetime('now', 'start of day')").fetchone()[0]
    con.close()
    return n


def pending_without_ai_review():
    con = connect()
    ids = [r[0] for r in con.execute("SELECT id FROM submissions WHERE status = 'pending' AND ai_review IS NULL ORDER BY id")]
    con.close()
    return ids


def versions():
    """{'catalog_version': n, 'uses_version': n}: one tiny query, run before each request."""
    con = connect()
    v = {r[0]: r[1] for r in con.execute("SELECT key, value FROM meta")}
    con.close()
    return v


def _bump(con, key):
    con.execute("INSERT INTO meta (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1", (key,))


def _bump_catalog_version(con):
    _bump(con, "catalog_version")


def get_uses():
    con = connect()
    uses = {r["idea_id"]: r["uses"] for r in con.execute("SELECT * FROM idea_uses")}
    con.close()
    return uses


def set_ai_review(sub_id, review):
    con = connect()
    con.execute("UPDATE submissions SET ai_review = ? WHERE id = ?", (json.dumps(review), sub_id))
    con.commit()
    con.close()


def get_submission(sub_id):
    con = connect()
    r = con.execute("SELECT * FROM submissions WHERE id = ?", (sub_id,)).fetchone()
    con.close()
    return dict(r) if r else None


def set_submission_status(sub_id, status, linked_idea_id=None):
    con = connect()
    con.execute("UPDATE submissions SET status = ?, linked_idea_id = ? WHERE id = ?", (status, linked_idea_id, sub_id))
    con.commit()
    con.close()


def add_community_idea(sub_id, f):
    """Turn an approved submission into a live idea. Returns its new id (c001, c002...)."""
    con = connect()
    n = con.execute("SELECT COALESCE(MAX(CAST(SUBSTR(id, 2) AS INTEGER)), 0) FROM community_ideas").fetchone()[0] + 1
    cid = f"c{n:03d}"
    con.execute(
        "INSERT INTO community_ideas (id, submission_id, title, hook, summary, how_it_works, place, result, setup_type,"
        " setup_by_platform, phone_support, difficulty, settings, goals, needs, contributor, source_url, original_text)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, sub_id, f["title"], f.get("hook") or f["title"], f["summary"], f.get("how_it_works") or f["summary"],
         f.get("place"), f.get("result"), f.get("setup_type") or "automation", f.get("setup_by_platform"),
         f.get("phone_support") or "any", f.get("difficulty") or "easy", json.dumps(f.get("settings") or []),
         json.dumps(f.get("goals") or []), json.dumps(f.get("needs") or []), f.get("contributor") or None,
         f.get("source_url") or None, f.get("original_text") or None))
    con.execute("UPDATE submissions SET status = 'approved', linked_idea_id = ? WHERE id = ?", (cid, sub_id))
    _bump_catalog_version(con)
    con.commit()
    con.close()
    return cid


def remove_community_idea(sub_id):
    """Take an approved idea out of the bank again (the submission becomes 'rejected')."""
    con = connect()
    r = con.execute("SELECT linked_idea_id FROM submissions WHERE id = ? AND status = 'approved'", (sub_id,)).fetchone()
    if r:
        con.execute("DELETE FROM community_ideas WHERE id = ?", (r[0],))
        con.execute("UPDATE submissions SET status = 'rejected', linked_idea_id = NULL WHERE id = ?", (sub_id,))
        _bump_catalog_version(con)
        con.commit()
    con.close()
    return bool(r)


def add_use(idea_id):
    con = connect()
    con.execute("INSERT INTO idea_uses (idea_id, uses) VALUES (?, 1) "
                "ON CONFLICT(idea_id) DO UPDATE SET uses = uses + 1", (idea_id,))
    uses = con.execute("SELECT uses FROM idea_uses WHERE idea_id = ?", (idea_id,)).fetchone()[0]
    _bump(con, "uses_version")
    con.commit()
    con.close()
    return uses
