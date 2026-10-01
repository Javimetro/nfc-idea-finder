"""AI review of a visitor's idea, so nobody has to check every one by hand.

Each submission gets three answers:
  1. Is it a real NFC idea at all? (spam, nonsense, unsafe -> not_an_idea)
  2. Is it already in the bank? (duplicate -> which idea)
  3. If it's new: a cleaned-up draft that goes live (title, hook, summary, needs...).

Two reviewers, picked with TAPWISE_REVIEWER:
  "claude" (default): one Claude call does all three.
  "hybrid": Jev (TypeSafe) makes the decisions (1, 2, and the needs/setup/difficulty/phone choices)
            and Claude only writes the text for ideas Jev says are new. Jev is much cheaper but
            can't write text. Falls back to "claude" if Jev is off or fails.
Only the idea text goes to either service, never names or emails.

Switched off (returns None) without any key or without the `anthropic` package; the site works
the same without it, ideas just wait on /admin."""
import json
import os
import time
import urllib.error
import urllib.request
from typing import List, Literal, Optional

try:
    import anthropic
    from pydantic import BaseModel
except ImportError:                        # running without the AI extras: AI review stays off
    anthropic = None
    BaseModel = object

MODEL = os.environ.get("TAPWISE_AI_MODEL", "claude-opus-5")
REVIEWER = os.environ.get("TAPWISE_REVIEWER", "claude")
JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"


class Writing(BaseModel):
    hook: str             # short curious title, e.g. "The Bike Lock That Remembers"
    title: str            # plain title, e.g. "Log where you parked your bike"
    summary: str          # one or two sentences for visitors
    place: str            # where the tag goes
    result: str           # what happens when you tap


class Draft(Writing):
    setup_type: Literal["automation", "link", "smarthome", "app", "maker"]
    difficulty: Literal["easy", "medium", "advanced"]
    phone_support: Literal["any", "iphone_only", "android_only"]
    needs: List[str]      # ids from the needs list


class Review(BaseModel):
    verdict: Literal["new", "duplicate", "not_an_idea"]
    duplicate_of: Optional[str]
    confidence: Literal["high", "medium", "low"]
    reason: str           # one sentence, shown to the admin
    draft: Optional[Draft]


SYSTEM = """You help run Tapwise, a website with a bank of everyday NFC tag ideas (tap a sticker with your phone and something useful happens).
Visitors suggest new ideas. You give each suggestion a first review so the site owner doesn't have to read every one.

Decide the verdict:
- "duplicate": the suggestion is essentially the same idea as one already in the bank: same place or trigger AND same result for the user, even in different words. A different angle (different place, different audience, a clearly different result) is NOT a duplicate. Set duplicate_of to that idea's id.
- "not_an_idea": spam, advertising, nonsense, off-topic, not about NFC tags/cards at all, or unsafe advice (e.g. storing passwords, crypto keys or unlock links on a tag anyone can scan).
- "new": a real NFC idea that the bank doesn't have yet.

confidence: "high" only when you are sure. For a duplicate, "high" means a reader would say "that's the same thing".
reason: one short plain sentence for the owner (for duplicates, say what is the same).
draft: only for "new" (otherwise null). Rewrite the idea in clean, friendly English, keep the visitor's idea (don't invent features), and pick 0-3 needs ids from the list that this idea would genuinely help with."""

WRITE_SYSTEM = """You write entries for Tapwise, a website with a bank of everyday NFC tag ideas (tap a sticker with your phone and something useful happens).
Rewrite the visitor's idea in clean, friendly English. Keep their idea exactly; don't invent features.
hook: a short curious title (e.g. "The Bike Lock That Remembers"). title: a plain title (e.g. "Log where you parked your bike").
summary: one or two sentences for visitors. place: where the tag goes (e.g. "on your bike lock"). result: what happens when you tap (e.g. "your phone saves your location")."""


def claude_enabled():
    return bool(anthropic and os.environ.get("ANTHROPIC_API_KEY"))


def jev_enabled():
    return bool(os.environ.get("TYPESAFE_API_KEY"))


def enabled():
    return claude_enabled()                # Claude is needed in both modes (hybrid: to write new ideas)


def _client():
    return anthropic.Anthropic(timeout=90.0) if claude_enabled() else None


def _suggestion(description, place):
    return description + (f"\nWhere the tag goes: {place}" if place else "")


def review(description, place, ideas, needs):
    """`ideas`: [{id, title, summary}], `needs`: [{id, label}]. Returns a dict, or None if AI is off/failed."""
    if REVIEWER == "hybrid" and jev_enabled():
        r = hybrid_review(description, place, ideas, needs)
        if r:
            return r
    return claude_review(description, place, ideas, needs)


# ------------------------------------------------------------------ Claude does everything
def claude_review(description, place, ideas, needs):
    client = _client()
    if not client:
        return None
    bank = "\n".join(f"{i['id']}: {i['title']}. {i['summary']}" for i in ideas)
    need_list = "\n".join(f"{n['id']}: {n['label']}" for n in needs)
    try:
        resp = client.messages.parse(
            model=MODEL,
            max_tokens=8000,
            output_config={"effort": "low"},
            system=SYSTEM,
            messages=[{"role": "user", "content":
                       f"<idea_bank>\n{bank}\n</idea_bank>\n\n<needs>\n{need_list}\n</needs>\n\n"
                       f"<visitor_suggestion>\n{_suggestion(description, place)}\n</visitor_suggestion>"}],
            output_format=Review,
        )
    except Exception as e:                     # network, rate limit, bad key: just leave it for later
        print("AI review failed:", type(e).__name__, e, flush=True)
        return None
    if resp.stop_reason == "refusal" or not resp.parsed_output:
        return None
    r = resp.parsed_output.model_dump()
    known = {i["id"] for i in ideas}
    if r["verdict"] == "duplicate" and r["duplicate_of"] not in known:
        r["verdict"], r["confidence"] = "new", "low"     # pointed at an idea that doesn't exist: don't trust it
    if r["draft"]:
        valid = {n["id"] for n in needs}
        r["draft"]["needs"] = [n for n in r["draft"]["needs"] if n in valid]
    r["model"] = MODEL
    r["engine"] = "claude"
    r["usage"] = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    return r


def claude_write(description, place):
    """Only the text of a new idea (hybrid mode). Returns a dict or None."""
    client = _client()
    if not client:
        return None
    try:
        resp = client.messages.parse(
            model=MODEL, max_tokens=4000, output_config={"effort": "low"}, system=WRITE_SYSTEM,
            messages=[{"role": "user", "content":
                       f"<visitor_suggestion>\n{_suggestion(description, place)}\n</visitor_suggestion>"}],
            output_format=Writing,
        )
    except Exception as e:
        print("AI writing failed:", type(e).__name__, e, flush=True)
        return None
    if resp.stop_reason == "refusal" or not resp.parsed_output:
        return None
    return resp.parsed_output.model_dump()


# ------------------------------------------------------------------ Jev decides, Claude writes
KINDS = {
    "real_idea": "A real, safe idea for using an NFC tag, sticker or card",
    "spam_or_ad": "Spam, advertising or self-promotion",
    "nonsense": "Nonsense, a test message, or not about NFC tags at all",
    "unsafe": "Unsafe advice, e.g. putting passwords, PINs, crypto keys or a door-unlock link on a tag anyone could scan",
}
SETUP_TYPES = {
    "automation": "A phone automation (Shortcuts on iPhone, MacroDroid or similar on Android) runs when the tag is tapped",
    "link": "The tag simply opens a link, joins wifi, shares a contact or sends a text",
    "smarthome": "The tap controls smart home devices (lights, locks, heating) through a smart home system",
    "app": "The tap opens or is handled by one specific app",
    "maker": "A build project with a Raspberry Pi, Arduino or an NFC reader",
}
DIFFICULTY = {
    "easy": "A beginner can set it up in a few minutes with a phone and a sticker",
    "medium": "Needs some fiddling: a multi-step automation or a smart home setup",
    "advanced": "Needs programming, electronics or a custom web app",
}
PHONES = {
    "any": "Works on both iPhone and Android",
    "iphone_only": "Only works on iPhone",
    "android_only": "Only works on Android",
}


def _label(conf):
    return "high" if conf >= 0.8 else "medium" if conf >= 0.5 else "low"


def jev_decide(description, place, ideas, needs):
    """One Jev call with every decision as a separate question. Returns a dict or None."""
    if not jev_enabled() or len(ideas) > 254:          # Choice takes up to 255 options (bank + "none")
        return None
    state = {"visitor_suggestion": description, "where_the_tag_goes": place or "not given"}
    questions = {
        "kind": {"type": "choice", "criteria": KINDS,
                 "instructions": "What kind of submission is the visitor_suggestion?"},
        "same_as": {"type": "choice",
                    "criteria": {**{i["id"]: f"{i['title']}. {i['summary']}" for i in ideas},
                                 "none": "None of these is the same idea"},
                    "instructions": "Which existing idea is the same idea as the visitor_suggestion: the tag is used in "
                                    "the same situation and the user gets the same result, even if it's worded "
                                    "differently? Choose none if no existing idea is the same idea."},
        "setup_type": {"type": "choice", "criteria": SETUP_TYPES,
                       "instructions": "How would someone most likely set up the visitor_suggestion?"},
        "difficulty": {"type": "choice", "criteria": DIFFICULTY,
                       "instructions": "How hard is the visitor_suggestion to set up?"},
        "phone_support": {"type": "choice", "criteria": PHONES,
                          "instructions": "Which phones can do the visitor_suggestion?"},
        **{f"need_{n['id']}": {"type": "noul",
                               "instructions": f"The visitor_suggestion would genuinely help someone who says: \"{n['label']}\""}
           for n in needs},
    }
    body = json.dumps({"state": state, "model": JEV_MODEL, "questions": questions}).encode()
    req = urllib.request.Request(JEV_URL, data=body, headers={
        "Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                out = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and attempt < 2:      # rate limited / overloaded: wait and retry
                time.sleep(2 ** (attempt + 1))
                continue
            print("Jev failed:", e.code, e.read()[:300], flush=True)
            return None
        except Exception as e:
            print("Jev failed:", type(e).__name__, e, flush=True)
            return None
    a = out["answers"]
    kind, same = a["kind"], a["same_as"]
    titles = {i["id"]: i["title"] for i in ideas}
    if kind["choice"] != "real_idea":
        verdict, dup, conf = "not_an_idea", None, kind["confidence"]
        reason = f"Jev: looks like {kind['choice'].replace('_', ' ')} ({kind['probabilities'][kind['choice']]:.0%})."
    elif same["choice"] != "none":
        verdict, dup, conf = "duplicate", same["choice"], same["confidence"]
        reason = f"Jev: same idea as \"{titles[dup]}\" ({same['probabilities'][dup]:.0%})."
    else:
        verdict, dup, conf = "new", None, min(kind["confidence"], same["confidence"])
        reason = f"Jev: a real idea ({kind['probabilities']['real_idea']:.0%}) that isn't in the bank yet."
    need_scores = sorted(((a[f"need_{n['id']}"]["noul"], n["id"]) for n in needs), reverse=True)
    return {
        "verdict": verdict, "duplicate_of": dup, "confidence": _label(conf), "reason": reason,
        "choices": {"setup_type": a["setup_type"]["choice"], "difficulty": a["difficulty"]["choice"],
                    "phone_support": a["phone_support"]["choice"],
                    "needs": [nid for score, nid in need_scores if score >= 0.5][:3]},
        "jev": {"model": out.get("model"), "usage": out.get("usage"), "kind": kind["probabilities"],
                "same_as_top": sorted(same["probabilities"].items(), key=lambda x: -x[1])[:3]},
    }


def hybrid_review(description, place, ideas, needs):
    d = jev_decide(description, place, ideas, needs)
    if not d:
        return None
    draft = None
    if d["verdict"] == "new":
        w = claude_write(description, place)
        if not w:
            return None                    # can't publish the raw text: let the idea wait and retry later
        draft = {**w, **d["choices"]}
    return {"verdict": d["verdict"], "duplicate_of": d["duplicate_of"], "confidence": d["confidence"],
            "reason": d["reason"], "draft": draft, "model": f"{d['jev']['model']} + {MODEL}",
            "engine": "hybrid", "jev": d["jev"]}
