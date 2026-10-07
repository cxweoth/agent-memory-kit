# editing-semantic-and-rule-files

## Memory Summary
- Visibility: Public
- Brief: When editing an existing semantic file or rule file: edit in place, save the old version, check pointers, update the Summary
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-10-07

## Memory Content

- **Before changing or deleting something, find what points to it and change those too.** When a definition changes, check downstream: `Prerequisites` depend on each other in order, so re-read every later prerequisite and every `Derived` definition to see whether it still holds; when a semantic entry changes, re-evaluate the procedurals derived from it; evidence in episodics that points to the old structure is allowed to break, and no mapping table is added for it.
- **Edit in place, and only the lines that need it.** Do not write a new entry next to the old one, do not leave tombstones such as "deleted" or "moved to", and do not reorder things while you are there; how a superseded old statement is removed follows the Semantic Delete rule. **After editing**: update the Summary too (`Brief`, `Admission`, `Updated`); only on the first change to this file today, save the whole old version into that layer's `2_semantic/history/` or `3_procedural/history/` (one copy per file per day; if that name already exists, do not save again); for rule files, also run `gen_dispatch.py` and `gen_index.py`.
