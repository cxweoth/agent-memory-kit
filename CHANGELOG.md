# Changelog

One entry per spec version. `VERSION` holds the current one.

An entry is marked **Action required** when an installed agent has to redo or add to work it already did (migration rules changed, a rule file was renamed, a tool's invocation changed). Agents read the entries newer than their `memory/spec/VERSION` on the sweep line; see `sweep-check-spec-updates.md`.

## v60 — 2026-10-07

Review pass after the first release. No rule changed; nothing to redo.

- Source spec gained a section pointing at this kit; the kit's `VERSION` follows the source's version number from here on.
- `memory_check.py`: the spec-version check now compares `memory/spec/VERSION` with the kit clone named in `MEMORY_ARCH.md` (`Kit clone` row), instead of warning on age.
- `mem_recall.py`: the tag vocabulary is read from `MEMORY_ARCH.md`, not hard-coded.
- `tally.py`: dropped an undocumented `skill_<name>.md` lookup.
- `memdoc.py`: runs on Python 3.9 (postponed annotations).
- Spec text: `memdoc.py --find` documented; rule pointers written as `3_procedural/<file>` so `memory_check.py` can resolve them; `<kit>/CHANGELOG.md`.
- `install.py`: the import episodic has every Episodic field.

## v59 — 2026-10-07

First public English release, translated from the source spec v59.

- All sections, the rules table (50 rules) and 16 rule files.
- Tools: `memory_check.py`, `memdoc.py`, `tally.py`, `gen_index.py`, `gen_dispatch.py`, `gen_spec.py`, `mem_mv.py`, `mem_recall.py`, and the `UserPromptSubmit/` hook scripts.
- `install.py` and `templates/` for setting up a new agent.
