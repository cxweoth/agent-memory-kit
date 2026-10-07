# sweep-check-spec-updates

## Memory Summary
- Visibility: Public
- Brief: On the sweep line, compare the kit's VERSION with memory/spec/VERSION; if they differ, read the new CHANGELOG.md entries, do what Action-required entries say, and regenerate the spec copy
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-10-07

## Memory Content

- **On the sweep line, check for spec updates.** Every release of the kit (`https://github.com/cxweoth/agent-memory-kit`) raises the number in its `VERSION` file by 1 and adds a `<kit>/CHANGELOG.md` entry saying which sections changed. On the sweep line, run `git pull` in your clone of the kit and compare the kit's `VERSION` with the first line of `memory/spec/VERSION`. If they differ: read every `<kit>/CHANGELOG.md` entry newer than your version and do what each entry marked **Action required** says; then rerun `gen_spec.py`, carry rule-file changes into `3_procedural/` as Add or Update per the rules, and copy the tools with `gen_spec.py --get` (review the diff before running them). The spec copy is always generated and never edited by hand; the kit does not push updates, the agent comes to read them.
