from . import rules, jev

ENGINES = {rules.NAME: rules, jev.NAME: jev}


def available_engines():
    return [{"name": e.NAME, "label": e.LABEL,
             "available": e.available() if hasattr(e, "available") else True}
            for e in ENGINES.values()]
