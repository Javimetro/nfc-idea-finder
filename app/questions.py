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
    "subtitle": "No tech knowledge needed. Here's all you need to know:",
    "points": [
        {"icon": "🏷️", "title": "A tiny sticker", "text": "NFC tags are stickers (or cards, keychains) that cost less than €1. No battery, they last for years."},
        {"icon": "📱", "title": "Your phone reads it", "text": "Almost every phone can. Hold it near the sticker, like paying with your card."},
        {"icon": "✨", "title": "Something happens", "text": "Open a page, start a timer, send a message, switch the lights off, share your wifi… you decide."},
        {"icon": "🧠", "title": "The tag is just a trigger", "text": "The sticker itself can't record, beep or light up. It only tells your phone what to do, and your phone does the work with its own screen, speaker, microphone and apps."},
    ],
    "outro": "Now tell us a bit about your day, and we'll find the taps worth trying.",
}


def _need_options(question):
    return [{"value": n["id"], "label": n["label"], **({"show_if": n["show_if"]} if n.get("show_if") else {})}
            for n in NEEDS if n["question"] == question]


# One screen per "world". show_if = only for people who picked one of these on screen 1.
# Worlds without show_if are shown to everyone (everybody has mornings and a home).
WORLDS = [
    ("mornings", "Mornings and evenings", "Pick anything that sounds like you. Skip if nothing fits.", None),
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
        "subtitle": "Pick everything that's true. This decides which questions come next.",
        "options": [
            {"value": "desk_job", "label": "I work at a desk / office"},
            {"value": "work_from_home", "label": "I work from home"},
            {"value": "student", "label": "I'm a student"},
            {"value": "drive", "label": "I drive a car"},
            {"value": "travel_often", "label": "I travel often"},
            {"value": "kids", "label": "I have kids"},
            {"value": "pets", "label": "I have pets"},
            {"value": "plants", "label": "I have plants or a garden"},
            {"value": "shared_home", "label": "I live with other people"},
            {"value": "workout", "label": "I exercise at home"},
            {"value": "hobbies", "label": "I have hobbies (music, games, crafts\u2026)"},
            {"value": "smart_home", "label": "I have smart lights, plugs or speakers"},
            {"value": "hub", "label": "I use Home Assistant or a smart home hub"},
            {"value": "business_owner", "label": "I run a business, shop or club"},
            {"value": "money", "label": "I'd like to earn money with NFC"},
        ],
    },
    *[_world_question(*w) for w in WORLDS],
    {
        "id": "phone", "type": "single", "required": True,
        "title": "What phone do you have?",
        "subtitle": "Some ideas work a bit differently on each.",
        "options": [
            {"value": "iphone", "label": "iPhone"},
            {"value": "android", "label": "Android", "hint": "Samsung, Pixel, Xiaomi, OnePlus\u2026"},
            {"value": "both", "label": "Both / other people's phones", "hint": "Family, guests or customers will tap too"},
        ],
    },
    {
        "id": "hands_on", "type": "single", "required": True,
        "title": "How much setup is OK for you?",
        "options": [
            {"value": "easy", "label": "It should just work", "hint": "A couple of minutes, no settings"},
            {"value": "medium", "label": "I can follow a short guide", "hint": "About 10\u201320 minutes with an app"},
            {"value": "advanced", "label": "I love tinkering", "hint": "Smart home setups, Raspberry Pi, building gadgets"},
        ],
    },
    {
        "id": "text", "type": "text",
        "title": "Anything that annoys you, again and again?",
        "subtitle": "Optional. One sentence helps, e.g. \u201cI can never find my keys\u201d or \u201cmy caf\u00e9 needs more reviews\u201d.",
        "placeholder": "Describe it in your own words\u2026",
    },
]
