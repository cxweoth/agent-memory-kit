# writing-semantic-files

## Memory Summary
- Visibility: Public
- Brief: When writing or editing a semantic file: principles, markers, tags, limits, and prohibitions
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-10-07

## Memory Content

- **Mark only exceptions.** Reliability: a `Source` you have not verified yourself is written as `unverified`. Type: the default is fact and is not marked; a derived entry writes `Inputs`, and a judgment writes `Premises`. Invalidation: write `Changes when` only for entries that depend on a decision or external state that can change.
- **The atom of semantic memory is one fact, not one file.** A file is only a container for facts that are read together and have **the same lifespan**: facts that always apply and facts that expire do not share a file.
- **Keep it short, and store only facts that are true now.** Semantic memory gets replaced by newer facts, so however complete the details are, they will be swapped out. Unfinished work counts too: record only that it "exists and is unresolved", and put the day it will be handled on the calendar; do not open a separate to-do list, and do not add a new layer.
- **The semantic layer is flat, and classification is by tag only**: many-to-many, no hierarchy among tags, used only for Semantic. The tag vocabulary is in your own `MEMORY_ARCH.md`, and each tag says "what kinds of questions route here". The `agent` tag marks the agent itself (memory system, tools, runtime environment) and never shares a file with a tag from the user's domain.
- **Hard limits for semantic files**: at most 200 lines per file (the number is `MAX_LINES` in `memdoc.py`); beyond that, split it or trim it. Fill in every Summary field per the Summary table; entries use only the fields in the "Fields allowed under an entry" table; inside `## Memory Content`, dates are allowed only in the `Confirmed` field and in episodic paths in `Source`, because a date in a sentence is narrative; leave no empty fields: omit a field with no content entirely, and do not write "none" as a placeholder.
