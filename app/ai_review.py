"""AI first look at a visitor's idea, so the admin doesn't have to check every one by hand.

One Claude call per submission answers three things:
  1. Is it already in the bank? (duplicate -> which idea)
  2. Is it a real NFC idea at all? (spam, nonsense, unsafe -> not_an_idea)
  3. If it's new: a cleaned-up draft for the approve form (title, hook, summary, needs...).

Switched off (returns None) when ANTHROPIC_API_KEY isn't set or the `anthropic` package isn't
installed; the site works the same without it."""
import os
from typing import List, Literal, Optional

try:
    import anthropic
    from pydantic import BaseModel
except ImportError:                        # running without the AI extras: AI review stays off
    anthropic = None
    BaseModel = object

MODEL = os.environ.get("TAPWISE_AI_MODEL", "claude-opus-5")


class Draft(BaseModel):
    hook: str             # short curious title, e.g. "The Bike Lock That Remembers"
    title: str            # plain title, e.g. "Log where you parked your bike"
    summary: str          # one or two sentences for visitors
    place: str            # where the tag goes
    result: str           # what happens when you tap
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


def enabled():
    return bool(anthropic and os.environ.get("ANTHROPIC_API_KEY"))


def _client():
    return anthropic.Anthropic(timeout=90.0) if enabled() else None


def review(description, place, ideas, needs):
    """`ideas`: [{id, title, summary}], `needs`: [{id, label}]. Returns a dict, or None if AI is off/failed."""
    client = _client()
    if not client:
        return None
    bank = "\n".join(f"{i['id']}: {i['title']}. {i['summary']}" for i in ideas)
    need_list = "\n".join(f"{n['id']}: {n['label']}" for n in needs)
    suggestion = description + (f"\nWhere the tag goes: {place}" if place else "")
    try:
        resp = client.messages.parse(
            model=MODEL,
            max_tokens=8000,
            output_config={"effort": "low"},
            system=SYSTEM,
            messages=[{"role": "user", "content":
                       f"<idea_bank>\n{bank}\n</idea_bank>\n\n<needs>\n{need_list}\n</needs>\n\n"
                       f"<visitor_suggestion>\n{suggestion}\n</visitor_suggestion>"}],
            output_format=Review,
        )
    except Exception as e:                     # network, rate limit, bad key: just leave it for the human
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
    return r
