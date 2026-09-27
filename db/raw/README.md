# Raw NotebookLM outputs

Exactly what NotebookLM returned, before any cleaning. Kept so the whole
database can be rebuilt and checked against the original extraction.

- `00_sources_inventory.json`: step 1 prompt (all sources)
- `batch*.json`: step 2 prompt, ~5 sources per batch
- `batch6_robles.json`: source added later (Stephen Robles video)
- `batch7`–`batch11`, `10_reddit_sources_inventory.json`: Reddit threads

Two books were part of the first batches and were later removed from the project, together with their extractions (batch 4 and part of batch 6).

The cleaned database is built from these by `scripts/build_db.py` → `db/*.json`.
