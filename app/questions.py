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
    ],
    "outro": "Now tell us a bit about your day, and we'll find the taps worth trying.",
}


def _need_options(question):
    return [{"value": n["id"], "label": n["label"], **({"show_if": n["show_if"]} if n.get("show_if") else {})}
            for n in NEEDS if n["question"] == question]


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
            {"value": "smart_home", "label": "I have smart lights, plugs or speakers"},
            {"value": "hub", "label": "I use Home Assistant or a smart home hub"},
            {"value": "business_owner", "label": "I run a business, shop or club"},
            {"value": "money", "label": "I'd like to earn money with NFC"},
        ],
    },
    {"id": "mornings", "type": "multi", "title": "How do your mornings go?",
     "subtitle": "Pick anything that sounds like you. Skip if nothing fits.", "options": _need_options("mornings")},
    {"id": "home", "type": "multi", "title": "And at home?",
     "subtitle": "The little annoyances are the best clues.", "options": _need_options("home")},
    {"id": "work", "type": "multi", "title": "Work, study and ideas",
     "subtitle": "Pick anything that sounds like you.", "options": _need_options("work")},
    {"id": "move", "type": "multi", "title": "On the move",
     "subtitle": "Car, travel, everyday errands.", "options": _need_options("move")},
    {"id": "health", "type": "multi", "title": "Habits and health",
     "subtitle": "Anything you'd like to make easier?", "options": _need_options("health")},
    {"id": "business", "type": "multi", "show_if": ["business_owner", "money"], "title": "About your business",
     "subtitle": "What would help most?", "options": _need_options("business")},
    {
        "id": "phone", "type": "single", "required": True,
        "title": "What phone do you have?",
        "subtitle": "Some ideas work a bit differently on each.",
        "options": [
            {"value": "iphone", "label": "iPhone"},
            {"value": "android", "label": "Android", "hint": "Samsung, Pixel, Xiaomi, OnePlus…"},
            {"value": "both", "label": "Both / other people's phones", "hint": "Family, guests or customers will tap too"},
        ],
    },
    {
        "id": "hands_on", "type": "single", "required": True,
        "title": "How much setup is OK for you?",
        "options": [
            {"value": "easy", "label": "It should just work", "hint": "A couple of minutes, no settings"},
            {"value": "medium", "label": "I can follow a short guide", "hint": "About 10–20 minutes with an app"},
            {"value": "advanced", "label": "I love tinkering", "hint": "Smart home setups, Raspberry Pi, building gadgets"},
        ],
    },
    {
        "id": "text", "type": "text",
        "title": "Anything that annoys you, again and again?",
        "subtitle": "Optional. One sentence helps, e.g. “I can never find my keys” or “my café needs more reviews”.",
        "placeholder": "Describe it in your own words…",
    },
]
