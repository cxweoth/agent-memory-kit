# Skeleton and Summary

<!-- Generated file; do not edit by hand. Source: Memory System Specification v60; generated on 2026-10-07 -->

`The three kinds side by side`

## The skeleton of every file

```
# Title
├ ## Memory Summary    fields: see the table below
└ ## Memory Content     Semantic splits it into entries: see the semantic file skeleton
```

- Level 2 has only **Memory Summary** and **Memory Content**, in that order; no subsection may appear before `## Memory Content`.

## The Summary at the top of every file

| Field | Used in | Value |
|---|---|---|
| Visibility | All three | Public / Private |
| Tags | Semantic | Which domains this file belongs to, comma-separated. The vocabulary is in `MEMORY_ARCH.md` |
| Brief | All three | One sentence. Episodic: what happened; Semantic: what this file holds; Procedural: what this rule says to do |
| Admission | Semantic | What may be written into this file, and what may not |
| Open when | Semantic | Which tasks should make you open this file |
| Occurred | Episodic | `YYYY-MM-DD HH:MM–HH:MM` plus the time zone |
| Transcript | Episodic | A path, marked "may be stale". **Never usable as a source** |
| Procedurals used | Episodic | Rule file names, possibly several. Accumulated by tally |
| Errors caught by | Episodic | `<source> N, <source> N`; no errors: `none`; filled in after the fact: `unrecorded` |
| Upstream | Semantic, Procedural | Which episodics it was extracted from; a Procedural derived from a semantic fact names that entry |
| Access | Procedural | **Boot**: read at the start of every conversation; lives in `CLAUDE.md`. **Triggered**: loaded only when a condition in `CLAUDE.md` holds, or when a semantic entry's `Before use` points to it; lives in `3_procedural/`. |
| Scope | Procedural | The deciding question: if a different agent did work for the same person, would this rule still be there? **universal**: yes; it is discipline every agent with this memory system should have. **this-user**: yes, because it exists because of who the user is. **this-role**: no; it exists because of this agent's job, and a different job replaces the whole layer. |
| Updated | Semantic, Procedural | `YYYY-MM-DD` |

- For each kind, the field order is the order of this table, from top to bottom.
