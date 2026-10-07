# rule-files-hold-only-rules

## Memory Summary
- Visibility: Public
- Brief: When writing or editing a rule file: one rule per file, how to filter content, how to write checks, how to read counts
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-10-07

## Memory Content

- **A check and a semantic entry point to each other.** The check's `Upstream` names the semantic entry it is derived from, and that entry's `Before use` points back to the check. The semantic fact a check relies on is not rewritten inside the check.
- **Every rule file must be reachable**: from `CLAUDE.md`, or from some semantic entry's `Before use`. The more often a rule is used, the earlier it goes.
- **Moving to another system**: take every rule file marked `Scope: universal`, and drop the `Upstream` field.
- **A rule file holds only what must be followed at the moment of acting and cannot be re-derived.** Scenario test: at the moment the action is about to happen, what do you need in front of you? Something that would not change your next action even if you knew it is not a rule; arbitrary conventions (formats, constants, thresholds) must be kept, and conclusions that can be re-derived are not kept. One rule per file, one point per line, imperative mood, no history. **Exception**: the few rules marked `Scope: this-role` that live in the boot layer are always loaded together, and splitting them would help neither finding nor counting them, so they may share one file whose `Brief` says which kind of action it covers; triggered-layer rules may not be merged, because a triggered-layer rule is found by its file name.
- **Examples in rule files use no project names, personal names, or private matters**; always say "the user" and "the agent". A rule that is itself about that project or role is exempt once it is marked `Scope: this-role`.
- **What becomes a check**: a "check this before use" derived from a semantic fact, and a ruling the agent has made. Checks go in the triggered layer; if the agent has a systematic bias on the topic, name the bias and put it first, and mark that file `Scope: this-role`.
