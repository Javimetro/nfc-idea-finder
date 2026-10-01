"""Instant "is this already in the bank?" hint. Free, local, no AI.

TF-IDF word matching: words that are rare in the bank ("wifi", "litter", "vinyl") count much more
than common ones ("door", "home"). Light stemming and a few synonyms help with everyday wording.
It's only a hint for the visitor (and a shortlist on /admin); the real duplicate check is Jev's.

Measured on scripts/review_cases_big.py (145 reworded duplicates): the right idea is in the hint
for 120 (83%), up from 100 (69%) with the old plain word overlap."""
import math
import re

STOPWORDS = set("""a an the and or but so to of in on at for with without from into onto by as up out off over
your yours you my mine our their his her its it is are was were be being been do does did am
this that these those i we they he she them us me can could should would will just when then than
where what who how which tag tags nfc sticker stickers phone phones each one instead also very
get gets got make makes put tap taps tapping tapped open opens if there here some any all""".split())

# everyday words -> the word the bank uses
SYNONYMS = {
    "wi": "wifi", "internet": "wifi", "router": "wifi", "medicine": "pill", "medication": "pill",
    "vitamin": "pill", "meds": "pill", "tablet": "pill", "lamp": "light", "bulb": "light", "song": "music",
    "playlist": "music", "spotify": "music", "album": "music", "record": "music", "vinyl": "music",
    "auto": "car", "vehicle": "car", "dashboard": "car", "dog": "pet", "cat": "pet", "kid": "child",
    "kids": "child", "children": "child", "toddler": "child", "daughter": "child", "son": "child",
    "bin": "trash", "rubbish": "trash", "garbage": "trash", "wheelie": "trash", "nightstand": "bed",
    "bedside": "bed", "headboard": "bed", "sleep": "bed", "bedtime": "bed", "tripadvisor": "review",
    "countdown": "timer", "minute": "timer", "linkedin": "contact",
}

THRESHOLD = 0.2       # below this, the match is too weak to show


def _stem(w):
    for suffix in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if w in STOPWORDS or len(w) < 3:
            continue
        w = SYNONYMS.get(w, w)
        w = SYNONYMS.get(_stem(w), _stem(w))
        out.append(w)
    return out


class Index:
    """Built once per catalog load; search() is a few microseconds per idea."""

    def __init__(self, ideas):
        self.ideas = ideas
        docs = [tokens(" ".join(filter(None, [i["title"], i["title"], i.get("hook"), i["summary"],
                                              i.get("place"), i.get("result")]))) for i in ideas]
        df = {}
        for d in docs:
            for w in set(d):
                df[w] = df.get(w, 0) + 1
        n = len(docs)
        self.unknown_idf = math.log(n + 1) + 1
        self.idf = {w: math.log((n + 1) / (c + 1)) + 1 for w, c in df.items()}
        self.vectors = [self._vector(d) for d in docs]

    def _vector(self, toks):
        tf = {}
        for w in toks:
            tf[w] = tf.get(w, 0) + 1
        v = {w: c * self.idf.get(w, self.unknown_idf) for w, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        return {w: x / norm for w, x in v.items()}

    def search(self, text, limit=5, min_score=THRESHOLD):
        q = self._vector(tokens(text))
        if not q:
            return []
        scored = []
        for idea, v in zip(self.ideas, self.vectors):
            s = sum(x * v.get(w, 0) for w, x in q.items())
            if s >= min_score:
                scored.append((s, idea))
        scored.sort(key=lambda x: -x[0])
        return scored[:limit]
