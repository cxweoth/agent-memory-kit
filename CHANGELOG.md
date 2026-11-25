# Changelog

One entry per spec version. `VERSION` holds the current one.

An entry is marked **Action required** when an installed agent has to redo or add to work it already did (migration rules changed, a rule file was renamed, a tool's invocation changed). Agents read the entries newer than their `memory/spec/VERSION` on the sweep line; see `sweep-check-spec-updates.md`.

## v62 — 2026-11-25

Covers source versions 61 and 62, published the same day (62 only fixed `due.py --done 0` deleting the last row).

**Action required**

1. Copy the tools again: `python3 memory/tools/gen_spec.py --get <kit> memory/tools`, and review the diff before running them. New: `UserPromptSubmit/due.py`, `UserPromptSubmit/boot_echo.py`. Changed: `UserPromptSubmit/emit.py`, `memory_check.py`. If you edited `emit.py` yourself, merge by hand instead of overwriting.
2. Regenerate `memory/spec/` and carry the rule-file changes into `3_procedural/` as Add or Update: new rule file `promises-go-in-the-due-list.md` (rule 52); `consolidating-episodics.md` gained rule 51; the wording of rules 3, 24, 31, 32 and 35 changed.
3. Add two items to your `MEMORY_ARCH.md` (see `templates/MEMORY_ARCH.md`): a "Weekly extraction day", and optionally an "Echo every turn" section of at most 6 lines.
4. Run `python3 memory/tools/memory_check.py` and go through "possibly stale, take a look": for each entry listed, look, and if it still holds, update its `Confirmed`.

What changed:

- Rule 3: "twice" is counted in episodics; two on the same day count, and `Upstream` lists both.
- Rule 51 (new) and rule 24: one fixed sweep line every week extracts all unconsolidated episodics into the semantic layer; stamp only when none are left.
- Rule 52 (new), `due.py`, `memory/due.json`: the agent's own promised to-dos with a due date surface in its context when due. Rule 35 now says where the handling day goes: the user's on the calendar, the agent's own in `due.json`.
- Rules 31 and 32, `memory_check.py`: entries whose `Changes when` or `Inputs` name a path that has commits after `Confirmed` are listed as possibly stale. The tool says "someone should look", not "this is wrong".
- `boot_echo.py`: reprints up to 6 boot-rule reminders from `MEMORY_ARCH.md` every turn, so they survive conversation compaction.
- Semantic memory gained "How to find things": a weekly-built keyword table plus a per-turn literal search. The two tools (`mem_keywords.py`, `mem_search.py`) are described but not shipped yet.

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
