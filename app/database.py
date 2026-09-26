"""SQLite database for the NFC Idea Finder.

The curated content (sources, ideas, links, tag profiles) lives as JSON files in /db
and is (re)loaded into SQLite every time the app starts. That way you edit JSON,
restart, and the site is up to date.

Visitor suggestions live only in SQLite and are never overwritten.
"""
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
    business_model TEXT, who_pays TEXT, startup_cost_level TEXT
);
CREATE TABLE IF NOT EXISTS idea_sources (
    idea_id TEXT, source_id TEXT, start_seconds INTEGER, end_seconds INTEGER, anchor_quote TEXT
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
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def load_content():
    """Replace all curated tables with the current JSON files (submissions untouched)."""
    load = lambda name: json.loads((JSON_DIR / f"{name}.json").read_text(encoding="utf-8"))
    con = connect()
    con.executescript(SCHEMA)
    for table in ("sources", "ideas", "idea_sources", "tag_profiles"):
        con.execute(f"DELETE FROM {table}")

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
            ":business_model,:who_pays,:startup_cost_level)", row)
    con.executemany(
        "INSERT INTO idea_sources VALUES (:idea_id,:source_id,:start_seconds,:end_seconds,:anchor_quote)",
        load("idea_sources"))
    con.executemany("INSERT INTO tag_profiles VALUES (?, ?)",
                    [(t["id"], json.dumps(t)) for t in load("tag_profiles")])
    con.commit()
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
    con.close()
    return {"ideas": ideas, "sources": sources, "tags": tags}


def add_submission(d):
    con = connect()
    con.execute(
        "INSERT INTO submissions (description, source_url, start_seconds, submitter_name, credit_ok, email, context)"
        " VALUES (?,?,?,?,?,?,?)",
        (d["description"], d.get("source_url"), d.get("start_seconds"), d.get("submitter_name"),
         1 if d.get("credit_ok") else 0, d.get("email"), json.dumps(d.get("context")) if d.get("context") else None))
    con.commit()
    con.close()


def list_submissions():
    con = connect()
    rows = [dict(r) for r in con.execute("SELECT * FROM submissions ORDER BY submitted_at DESC")]
    con.close()
    return rows
