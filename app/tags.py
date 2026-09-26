"""Tag matcher: turns an idea's needs + the visitor's conditions into ONE tag profile.

Deliberately plain rules, no AI: the recommendation always points to a profile
the user wrote and checked by hand (db/tag_profiles.json)."""


def pick_tag(idea, answers, tags_by_id):
    needs = idea.get("tag_needs") or {}
    cond = set(answers.get("conditions") or [])
    form = needs.get("form")
    why = []

    if idea["kind"] == "maker":
        return tags_by_id["t_reader_kit"], ["you build your own reader"]
    if needs.get("secure") or "no_copy" in cond:
        return tags_by_id["t_ntag424"], ["it must be hard to copy"]
    if needs.get("on_metal") or "metal" in cond:
        why.append("it goes on metal")
        return tags_by_id["t_antimetal"], why
    if form == "card" or "card" in cond:
        return tags_by_id["t_card"], ["wallet-sized card"]
    if form == "keyfob" or "wearable" in cond:
        return tags_by_id["t_keyfob"], ["you carry it with you"]
    if form == "wristband":
        return tags_by_id["t_wristband"], ["worn on the wrist"]
    if needs.get("waterproof") or form == "epoxy_disc" or cond & {"wet", "public"}:
        if "wet" in cond or needs.get("waterproof"):
            why.append("it has to survive water")
        if "public" in cond:
            why.append("lots of people will tap it")
        return tags_by_id["t_epoxy"], why or ["tough and waterproof"]
    if needs.get("memory") in ("medium", "large"):
        return tags_by_id["t_ntag215_sticker"], ["it stores more data (wifi, contact, text)"]
    return tags_by_id["t_ntag213_sticker"], ["a simple trigger or link: the cheapest tag works"]
