"""The interview: questions about everyday life, NOT about NFC.

Visitors don't need to know what NFC can do. They tell us about their day,
and each "annoyance" they pick is a *need* (db/needs.json) that points to
the NFC ideas that solve it.

show_if: only show a question/option if the visitor picked one of these
facts in the first question ("about").
"""
import json
from pathlib import Path

NEEDS = json.loads((Path(__file__).resolve().parent.parent / "db" / "needs.json").read_text(encoding="utf-8"))
NEEDS_BY_ID = {n["id"]: n for n in NEEDS}

INTRO = {
    "id": "intro", "type": "intro",
    "title": "NFC in 20 seconds",
    "story_title": "A use example",
    "story": "Monday, 8:05. You're at the door, keys in hand, sure you're forgetting something. "
             "You tap your phone on a little sticker by the door, and your \u201cbefore you go\u201d checklist pops up. "
             "That sticker is an NFC tag.",
    "points": [
        {"icon": "🏷️", "title": "What it is", "text": "A sticker, card or keychain with a tiny chip. The same tech as tapping to pay, your bus card or a hotel key."},
        {"icon": "🔋", "title": "No battery", "text": "When your phone gets close, it powers the tag for a split second and reads it."},
        {"icon": "📱", "title": "Your phone does the work", "text": "The tag just says \u201cgo\u201d. Your phone opens the app, starts the timer or shows the list you chose."},
    ],
    "rule": "The golden rule: put the tag where the task happens. A laundry timer on the washer, a pill tracker on the pill bottle, the shopping list on the fridge.",
    "outro": "Now tell us a bit about your day, and we'll find the taps worth trying.",
}


def _need_options(question):
    return [{"value": n["id"], "icon": n.get("icon"), "label": n.get("short") or n["label"], "hint": n["label"],
             **({"show_if": n["show_if"]} if n.get("show_if") else {})}
            for n in NEEDS if n["question"] == question]


# One screen per "world". show_if = only for people who picked one of these on screen 1.
# Worlds without show_if are shown to everyone (everybody has mornings and a home).
WORLDS = [
    ("mornings", "Mornings and evenings", "Tap what sounds like you. Skip if nothing fits.", None),
    ("home", "At home", "The little annoyances are the best clues.", None),
    ("kids", "With the kids", "Pick anything that sounds like your family.", ["kids"]),
    ("pets", "Your pets", "Pick anything that sounds familiar.", ["pets"]),
    ("plants", "Plants and garden", "Pick anything that sounds like you.", ["plants"]),
    ("smarthome", "Your smart home", "You have smart gear, so taps can do even more.", ["smart_home", "hub"]),
    ("desk", "Work and study", "Pick anything that sounds like your workday.", ["desk_job", "work_from_home", "student"]),
    ("car", "In the car", "Pick anything that sounds like you.", ["drive"]),
    ("out", "Out and about", "Errands, travel and everyday bits.", None),
    ("health", "Habits and health", "Anything you'd like to make easier?", None),
    ("hobbies", "Hobbies and fun", "Pick anything that sounds like you.", ["hobbies"]),
    ("business", "About your business", "What would help most?", ["business_owner", "money"]),
]


def _world_question(key, title, subtitle, show_if):
    q = {"id": key, "type": "multi", "title": title, "subtitle": subtitle, "options": _need_options(key)}
    if show_if:
        q["show_if"] = show_if
    return q


QUESTIONS = [
    INTRO,
    {
        "id": "about", "type": "multi",
        "title": "First, a little about you",
        "subtitle": "Tap everything that fits you.",
        "options": [
            {"value": "desk_job", "icon": "💼", "label": "I work at a desk / office"},
            {"value": "work_from_home", "icon": "🏡", "label": "I work from home"},
            {"value": "student", "icon": "🎓", "label": "I'm a student"},
            {"value": "drive", "icon": "🚗", "label": "I drive a car"},
            {"value": "travel_often", "icon": "✈️", "label": "I travel often"},
            {"value": "kids", "icon": "🧒", "label": "I have kids"},
            {"value": "pets", "icon": "🐾", "label": "I have pets"},
            {"value": "plants", "icon": "🪴", "label": "I have plants or a garden"},
            {"value": "shared_home", "icon": "👥", "label": "I live with other people"},
            {"value": "workout", "icon": "🏋️", "label": "I exercise at home"},
            {"value": "hobbies", "icon": "🎨", "label": "I have hobbies (music, games, crafts\u2026)"},
            {"value": "smart_home", "icon": "💡", "label": "I have smart lights, plugs or speakers"},
            {"value": "hub", "icon": "🏠", "label": "I use Home Assistant or a smart home hub"},
            {"value": "business_owner", "icon": "🏪", "label": "I run a business, shop or club"},
            {"value": "money", "icon": "💶", "label": "I'd like to earn money with NFC"},
        ],
    },
    *[_world_question(*w) for w in WORLDS],
    {
        "id": "phone", "type": "single", "required": True,
        "title": "What phone do you have?",
        "subtitle": "Some ideas work a bit differently on each.",
        "options": [
            {"value": "iphone", "icon": "📱", "label": "iPhone"},
            {"value": "android", "icon": "🤖", "label": "Android", "hint": "Samsung, Pixel, Xiaomi, OnePlus\u2026"},
            {"value": "both", "icon": "👥", "label": "Both / other people's phones", "hint": "Family, guests or customers will tap too"},
        ],
    },
    {
        "id": "hands_on", "type": "single", "required": True,
        "title": "How much setup is OK for you?",
        "options": [
            {"value": "easy", "icon": "⚡", "label": "It should just work", "hint": "A couple of minutes, no settings"},
            {"value": "medium", "icon": "🛠️", "label": "I can follow a short guide", "hint": "About 10\u201320 minutes with an app"},
            {"value": "advanced", "icon": "🔧", "label": "I love tinkering", "hint": "Smart home setups, Raspberry Pi, building gadgets"},
        ],
    },
    {
        "id": "text", "type": "text",
        "title": "Anything that annoys you, again and again?",
        "subtitle": "Optional. One sentence helps, e.g. \u201cI can never find my keys\u201d or \u201cmy caf\u00e9 needs more reviews\u201d.",
        "placeholder": "Describe it in your own words\u2026",
    },
]
