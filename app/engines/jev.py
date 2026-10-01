"""Jev engine (TypeSafe AI) — placeholder.

Plan: keep the rules engine's filters (phone, hands-on, smart home), then ask Jev to
SCORE how well each remaining idea fits the visitor's answers, and re-rank by that
score. Only quiz answers are sent, never names or emails.

To finish: read the official API reference (https://docs.typesafe.ai), put the key
in the environment as TYPESAFE_API_KEY, and implement `score_fit` below.
"""
import os

NAME = "jev"
LABEL = "Jev (TypeSafe AI)"


def available():
    return bool(os.environ.get("TYPESAFE_API_KEY"))


def score_fit(answers, ideas):
    raise NotImplementedError("Jev engine not wired yet. See docstring.")


def rank(catalog, answers):
    from . import rules
    candidates = rules.rank(catalog, answers)[:30]      # cheap pre-filter
    scores = score_fit(answers, [c[1] for c in candidates])
    return sorted(((scores[i], *c[1:]) for i, c in enumerate(candidates)), key=lambda x: -x[0])
