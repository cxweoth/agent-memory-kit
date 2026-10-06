# Memory location

<!-- Generated file; do not edit by hand. Source: Memory System Specification v59; generated on 2026-10-07 -->

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
└── tools/
data/
```

- `1_episodic/consolidated/`: episodics that have been fully extracted. No subfolders below it.
- `2_semantic/history/`, `3_procedural/history/`: old versions and retired files. Flat, with no subfolders; file name `<original-name>_<YYYY-MM-DD>.md`. **At most one copy per file per day, holding the file as it was before today's first change**; later changes on the same day are not saved again, because git has the intermediate states. A retired file moves in whole, overwriting any file with the same name.
- `tools/`: the memory tools.
- `data/`: **not memory**; raw material.

## Each agent's own MEMORY_ARCH.md

| What | Content |
|---|---|
| Memory owner | What this agent is called, and who its user is |
| Tag vocabulary | One row per tag, saying "what kinds of questions route here" |
| Error sources | The names allowed in `Errors caught by`, matching `SOURCES` in `memory/tools/tally.py` exactly |
| Paths | Where this agent's memory root is; the spec copy is in `memory/spec/` |

- **This spec covers what all agents share; `MEMORY_ARCH.md` holds only the settings that belong to this agent alone.** Anything the spec already says is not written a second time: point to `memory/spec/` instead.
- Rules that belong only to this agent do not go in `MEMORY_ARCH.md`; they go in the agent's own `3_procedural/`, marked `Scope: this-user` or `Scope: this-role`.
