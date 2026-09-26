# Raw NotebookLM outputs

Exactly what NotebookLM returned, before any cleaning. Kept so the whole
database can be rebuilt and checked against the original extraction.

- `00_sources_inventory.json`: step 1 prompt (all sources)
- `batch*.json`: step 2 prompt, ~5 sources per batch
- `batch6_*`: sources added later (Stephen Robles video, Kurniawan book)

The cleaned database is built from these by `scripts/build_db.py` → `db/*.json`.
