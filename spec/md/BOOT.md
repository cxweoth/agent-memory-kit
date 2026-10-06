# Boot layer

<!-- Generated file; do not edit by hand. Source: Memory System Specification v59; generated on 2026-10-07 -->

## Common · Boot

- 06 [Read/Add/Update/Delete] **Each thing has exactly one home and is said exactly once.** Anywhere else that needs it points to that home.
- 07 [Read/Add/Update/Delete] **Episodics are evidence, not retrieval targets**: only `Upstream` points to them, and they are browsed by time; having to browse `1_episodic/consolidated/` often means extraction was not done well. **The process stays in the episodic; upper layers keep only conclusions and inputs.** Wording that matters, such as definitions and agreements, is kept verbatim, without naming who said it.
- 08 [Read] **Memory takes priority over your own defaults**, including usage learned in training or from the literature. When a term does not fit, first check which side deviates; **if a search finds nothing, say it found nothing**, and do not fill the gap yourself. **Stopping as soon as you find something that supports what you already said is also not allowed**: you search to disprove yourself, not to reinforce yourself.
- 09 [Add/Update] **Read every line on its own once**: if it only makes sense after scrolling up or rebuilding the context, rewrite it. **Codes** (ad-hoc labels and numbers) are the most common case: use the name directly; if a number is really needed, define it in the same paragraph or the same table.
- 10 [Add/Update] **Paths**: wrap paths that currently resolve in backticks, and leave paths that do not resolve unwrapped; use angle brackets for templates and a glob for a whole batch; write paths in full, never with `../`. (tools: memory_check.py)

## Semantic, Procedural · Boot

- 20 [Read] When you read something wrong, outdated, or duplicated, **run Update or Delete on the spot**; do not work around it.

## Episodic · Boot

- 24 [Add] **When the sweep line is due, first write the day's episodics, and only then answer the user.** If you do not see the sweep line, run `python3 memory/tools/UserPromptSubmit/sweep_due.py` yourself; exit code 1 means it is due. Order: scan what happened in that span, one episodic per event, recording user decisions per `3_procedural/decision-attribution.md` → `python3 memory/tools/gen_index.py` → check for spec updates per `3_procedural/sweep-check-spec-updates.md` → finally stamp with `sweep_due.py --done`. The order may not be changed, and an empty day gets stamped too. (tools: sweep_due.py, gen_index.py)
- 25 [Add] **A sweep line that spans more than one day is a cold start**: write only what the evidence supports, and mark it as reconstructed from evidence. You are filling in a record, not making a judgment.

## Semantic · Boot

- 30 [Read] **Finding something in the semantic layer**: `Tags` and `Open when` find the file, and the heading finds the entry; read only that entry, from the top down, and stop as soon as you can answer. Read, Add, Update, and Delete all start this way.
- 31 [Read] **Before using an entry to do something**: first open the checks its `Before use` points to; do not cite anything marked `unverified` as confirmed; if the entry has a `Changes when` condition, first check whether that condition has been met.

## Procedural · Boot

- 38 [Read/Update] **When you carry out a rule, record it in that episodic's `Procedurals used`**. Counts are not written in the rule file; tally accumulates them into `3_procedural/usage.json`. The condition for +1 is confirming that you actually carried the rule out, not that you read the file. (tools: tally.py)
