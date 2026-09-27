"""Rules engine: no AI, free, instant, offline. The baseline every AI engine has to beat.

How it ranks:
1. Collect the visitor's NEEDS: the everyday annoyances they ticked, plus needs
   whose keywords appear in their free text.
2. Every need points to ideas (db/needs.json) -> those ideas get big points,
   and we remember WHY (the need), so the results page can explain it.
3. Drop ideas that can't work for them (wrong phone, far too much setup),
   and lower ideas that need smart home gear they don't have.
4. Ideas nobody asked for can still show up as "popular with people like you"
   if they fit the visitor's life (car, desk, kids...).
"""
import re

import questions

NAME = "rules"
LABEL = "Rules (no AI)"

LEVEL = {"easy": 0, "medium": 1, "advanced": 2}
# facts from the "about you" question -> settings used in the ideas table
FACT_SETTINGS = {
    "desk_job": {"office"}, "work_from_home": {"office", "home"}, "student": {"office"},
    "drive": {"car"}, "travel_often": {"travel"}, "kids": {"home"}, "pets": {"pets"},
    "plants": {"outdoors", "home"}, "shared_home": {"home"}, "workout": {"health"},
    "smart_home": {"home"}, "hub": {"home"}, "hobbies": {"home", "events"}, "business_owner": {"shop", "restaurant", "events"},
    "money": {"events", "shop"},
}


def collect_needs(answers):
    """Returns {need_id: 'why' text} from ticked options and free-text keywords."""
    picked = {}
    for q in questions.QUESTIONS:
        if q["type"] != "multi" or q["id"] == "about":
            continue
        for need_id in answers.get(q["id"]) or []:
            if need_id in questions.NEEDS_BY_ID:
                picked[need_id] = "You said " + questions.NEEDS_BY_ID[need_id]["you_said"] + "."
    text = (answers.get("text") or "").strip()
    low = text.lower()
    if low:
        for n in questions.NEEDS:
            if n["id"] not in picked and any(re.search(r"\b" + re.escape(k), low) for k in n["keywords"]):
                picked[n["id"]] = f"You wrote: “{text[:120]}”."
    return picked


def _smart_home_need(idea):
    """Does this idea need smart home gear? Uses the idea's setup type, not guesswork on text."""
    if idea.get("setup_type") != "smarthome":
        return None
    s = (idea["setup_by_platform"] or "").lower()
    return "hub" if s.startswith(("home assistant", "home automation hub")) else "some"


def _feasibility(idea, a, facts):
    """Returns (score adjustment, warnings) or None if the idea can't work for this visitor."""
    s, warnings = 0.0, []
    ps, phone = idea["phone_support"], a.get("phone")
    mismatch = (phone == "iphone" and ps == "android_only") or (phone == "android" and ps == "iphone_only")
    if mismatch and "share_info" in (idea["goals"] or []):
        # other people (guests, customers) tap these, so YOUR phone doesn't decide
        s -= 1
        warnings.append("Works best for guests with " + ("Android" if ps == "android_only" else "iPhone"))
    elif mismatch:
        return None
    if phone == "both" and ps in ("android_only", "iphone_only"):
        s -= 2
        warnings.append("Only works on " + ("Android" if ps == "android_only" else "iPhone"))

    gap = LEVEL.get(idea["difficulty"], 0) - LEVEL.get(a.get("hands_on", "medium"), 1)
    if gap >= 2:
        return None
    if gap == 1:
        s -= 3
        warnings.append("Needs a bit more setup than you wanted")
    if idea["kind"] == "maker" and a.get("hands_on") != "advanced":
        return None

    have = "hub" if "hub" in facts else ("some" if "smart_home" in facts else "none")
    need = _smart_home_need(idea)
    if need and have == "none":
        s -= 4
        warnings.append("Needs smart home gear")
    elif need == "hub" and have == "some":
        s -= 2
        warnings.append("Needs a hub like Home Assistant")
    return s, warnings


def rank(catalog, answers):
    """Returns a list of (score, idea, why, warnings), best first.
    `why` is a list of {you_said, pitch}: empty means nobody asked for it."""
    facts = set(answers.get("about") or [])
    needs = collect_needs(answers)
    life_settings = set().union(*(FACT_SETTINGS.get(f, set()) for f in facts)) if facts else set()
    is_business = bool(facts & {"business_owner", "money"})

    ranked = []
    for idea in catalog["ideas"]:
        if idea["status"] == "hidden":
            continue
        feas = _feasibility(idea, answers, facts)
        if feas is None:
            continue
        score, warnings = feas

        # 1) needs -> the heart of the ranking
        why = []
        for need_id, said in needs.items():
            pitch = questions.NEEDS_BY_ID[need_id]["ideas"].get(idea["id"])
            if not pitch and need_id in (idea.get("needs") or []):
                pitch = idea["summary"]                  # community idea linked to this need by the admin
            if pitch:
                score += 10
                why.append({"need": need_id, "you_said": said, "pitch": pitch})

        # 2) small context bonuses
        score += min(len(life_settings & set(idea["settings"] or [])), 2)
        if not is_business and idea["kind"] == "business":
            score -= 6
        if is_business and set(idea["audience"]) & {"business_customers", "nfc_as_business"}:
            score += 2
        score += min(0.5 * (len(idea["sources"]) - 1), 1.5)       # explained by several creators

        ranked.append((score, idea, why, warnings))
    ranked.sort(key=lambda x: -x[0])
    return ranked
