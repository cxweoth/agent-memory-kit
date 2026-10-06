# Changelog

One entry per spec version. `VERSION` holds the current one.

An entry is marked **Action required** when an installed agent has to redo or add to work it already did (migration rules changed, a rule file was renamed, a tool's invocation changed). Agents read the entries newer than their `memory/spec/VERSION` on the sweep line; see `sweep-check-spec-updates.md`.

## v59 — 2026-10-07

First public English release, translated from the source spec v59.

- All sections, the rules table (50 rules) and 16 rule files.
- Tools: `memory_check.py`, `memdoc.py`, `tally.py`, `gen_index.py`, `gen_dispatch.py`, `gen_spec.py`, `mem_mv.py`, `mem_recall.py`, and the `UserPromptSubmit/` hook scripts.
- `install.py` and `templates/` for setting up a new agent.
