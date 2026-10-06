# before-adding-memory

## Memory Summary
- Visibility: Public
- Brief: Before adding any memory: whether to keep it, what its upstream is, whether each line should stay
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-09-20

## Memory Content

- **Conversation events → `1_episodic/`: extract**. Write it when it happens; waiting too long is hoarding. One event per episodic, and one conversation can produce several; store a summary, not the transcript. Whether to record it at all follows the Add rules.
- **`1_episodic/` → `2_semantic/`: extract; the only way in.** An event yields facts that carry no time; when a semantic fact changes, it is necessarily because some episodic happened.
- **`1_episodic/` → `3_procedural/`: count.** Compiled from repeated failures: **the same kind of error twice or more**; a one-off error goes only into `1_episodic/`.
- **`2_semantic/` → `3_procedural/`: derive.** From a known fact, infer "so this is what to do". No repetition is needed, but it **must name the semantic fact it is derived from**.
- **Set directly by the user → `3_procedural/`**. The user says on the spot how something should be done, and the agent records it. No repetition or derivation is needed, but **the user's exact words and the date must be quotable** (they live in the upstream episodic); if they cannot be quoted, this way in does not apply. **The exact words live only in that episodic, never in the rule file**; the rule file keeps only the action.
- **Ask two questions before keeping anything**: In what future situation will it be needed, and what cue will be used to find it then? Would deleting it cause an error, or only lose a reminder? Keep it only if both questions have answers. Ask this of every line and every section.
- **Upstream comes first.** Memory that cannot name its upstream is not allowed: it was made up on a hunch.
