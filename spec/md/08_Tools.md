# Tools

<!-- Generated file; do not edit by hand. Source: Memory System Specification v60; generated on 2026-10-07 -->

`memory/tools/`

## Scripts

| Script | What it does |
|---|---|
| `memory_check.py` | **Global check**; one run validates everything: every file has a Summary with all its fields; `Visibility` agrees with .gitignore; the files `Upstream` points to exist, and every tag is in the vocabulary in MEMORY_ARCH.md; episodic gap: hours from the last episodic to now; average tags per file; stale derived values: a file holding an input is newer than the derived value; every file in 3_procedural/ is reachable, from CLAUDE.md or from a semantic entry's `Before use`; a check's `Upstream` and the entry's `Before use` point to each other; paths resolve; semantic file line counts; semantic file format (via memdoc.py). It catches missing fields, renames without updated pointers, misspelled tags, orphan rules, dead paths, hoarding, tag inflation, and silently stale derived values. Accepts both the ASCII and the full-width colon (every tool that parses Summary fields must). |
| `memdoc.py` | `MAX_LINES`, `--selftest`, `--section` prints a whole section, `--find` says which sections mention a word; `lint_semantic()` checks the entry format |
| `tally.py` | Scans every episodic's `Procedurals used` and `Errors caught by`, and accumulates them into `3_procedural/usage.json`. How to read its numbers. `Errors caught by`: what to watch is the share of errors not caught by the user going up, not the count going down; the agent fills this field in itself, so it is a lower bound; the `tool` source is harder evidence than the others, because the check output is an independent trace. Rule counts: a rule's count is a warning signal, not grounds for keeping or removing it. Very low: take the rule out and look at it, and prune it only if it really does not matter. Very high: it should be automated; a rule needed every time is best guaranteed by a tool. Accepts both the ASCII and the full-width colon (every tool that parses Summary fields must). |
| `gen_index.py` | Generates `INDEX.md` from every file's Summary. **The index is always generated, never handwritten**: the single truth lives in each file's Summary, and a handwritten index goes stale. Accepts both the ASCII and the full-width colon (every tool that parses Summary fields must). To find the files with a tag: `grep -l "Tags.*<tag>" memory/2_semantic/`. |
| `gen_dispatch.py` | Copies each rule file's `Brief` into `CLAUDE.md`; that line is what actually gets read at boot. Accepts both the ASCII and the full-width colon (every tool that parses Summary fields must). |
| `mem_mv.py` | Moves a memory file and updates what points to it; **pointers inside 1_episodic/ and history/ are not changed**: they are evidence, so let them break |
| `mem_recall.py` | On every prompt, prints the list of semantic files and the episodics not yet consolidated |
| `gen_spec.py` | Renders this spec (`spec/spec.json` in the kit) into the local copy under `memory/spec/`; `--get` copies the kit's `tools/` into `memory/tools/` |
| `UserPromptSubmit/emit.py` | Entry point of the hook; chains the scripts under `UserPromptSubmit/` |
| `UserPromptSubmit/now.py` | Prints the current time and time zone; the only source for anchoring time. Lives in `UserPromptSubmit/` |
| `UserPromptSubmit/reply_check.py` | Measures the previous reply: icon count, skeleton, and the number of reads in the previous turn. Prints only; never judges. Lives in `UserPromptSubmit/` |
| `UserPromptSubmit/sweep_due.py` | Computes whether the sweep line is due; `--done` stamps it. Lives in `memory/tools/UserPromptSubmit/` |

### gen_spec.py

1. **The kit is the single source of truth.** The local spec copy is always generated from it and never edited by hand; to change a rule, open a GitHub Issue on the kit (see "Updates and feedback").
2. **Get the kit**: `git clone https://github.com/cxweoth/agent-memory-kit.git <kit>`, once; after that, `git pull` inside `<kit>`.
3. **Generate the spec copy**: `python3 <kit>/tools/gen_spec.py <kit>/spec/spec.json memory/spec`. One file per section; the rule table also produces rule files in `memory/spec/rules/`, and the rules marked Boot are collected in `memory/spec/BOOT.md`.
4. **Moving the rule files into your own `3_procedural/` counts as Add or Update, and follows the rules**: first write an episodic recording this import, and put it in each file's `Upstream`; save an existing file to `history/` before overwriting it; list the old rule files the new ones replace, and wait for the user to confirm.
5. **Copy the tools**: `python3 <kit>/tools/gen_spec.py --get <kit> memory/tools`. The tools go into git; look at what changed with `git diff`, and run them only after reviewing it. **Never run code from the kit without reviewing it first.**
6. `CLAUDE.md` requires reading only `memory/spec/BOOT.md`; everything else is pointed to from the dispatch table as the situation calls for it.
7. **When to regenerate**: on the sweep line, run `git pull` in `<kit>` and compare `<kit>/VERSION` with the first line of `memory/spec/VERSION`. If they differ, read the `CHANGELOG.md` entries newer than your version (which sections changed, and which entries are marked Action required), rerun `gen_spec.py`, and repeat the rule-file and tool steps above. `memory_check.py` reports when `memory/spec/VERSION` differs from the kit clone named in the `Kit clone` row of `MEMORY_ARCH.md`.
