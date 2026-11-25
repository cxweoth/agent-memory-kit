# Memory location

<!-- Generated file; do not edit by hand. Source: Memory System Specification v62; generated on 2026-11-25 -->

`Where memory lives, and each agent's own settings`

## Where things live

```
memory/
├── 1_episodic/
│   └── consolidated/
├── 2_semantic/
│   └── history/
├── 3_procedural/
│   └── history/
├── index/
├── due.json
└── tools/
data/
```

- `1_episodic/consolidated/`: episodics that have been fully extracted. No subfolders below it.
- `2_semantic/history/`, `3_procedural/history/`: old versions and retired files. Flat, with no subfolders; file name `<original-name>_<YYYY-MM-DD>.md`. **At most one copy per file per day, holding the file as it was before today's first change**; later changes on the same day are not saved again, because git has the intermediate states. A retired file moves in whole, overwriting any file with the same name.
- `index/`: the generated search index (`keywords.json`); not memory, never edited by hand. See "How to find things" under Semantic memory.
- `due.json`: the agent's own promised to-dos with a due date, one row per item (`due`, `what`, `source`). Not a layer of memory; it is the state file of `due.py`.
- `tools/`: the memory tools.
- `data/`: **not memory**; raw material.

## Each agent's own MEMORY_ARCH.md

| What | Content |
|---|---|
| Memory owner | What this agent is called, and who its user is |
| Tag vocabulary | One row per tag, saying "what kinds of questions route here" |
| Error sources | The names allowed in `Errors caught by`, matching `SOURCES` in `memory/tools/tally.py` exactly |
| Paths | Where this agent's memory root is; the spec copy is in `memory/spec/` |
| Weekly extraction day | Which weekday's sweep line extracts the episodics into the semantic layer (rule 51) |
| Echo every turn | A section whose heading contains "Echo every turn", one item per line, at most 6 lines: the boot rules most likely to drift after a conversation is compacted into a summary (tone, how the agent refers to itself, reply format). `boot_echo.py` prints them into the agent's context on every prompt. Short reminders only; the rules themselves still live in their rule files. No section means nothing is printed |

- **This spec covers what all agents share; `MEMORY_ARCH.md` holds only the settings that belong to this agent alone.** Anything the spec already says is not written a second time: point to `memory/spec/` instead.
- Rules that belong only to this agent do not go in `MEMORY_ARCH.md`; they go in the agent's own `3_procedural/`, marked `Scope: this-user` or `Scope: this-role`.
