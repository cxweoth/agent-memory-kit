# Rules

<!-- Generated file; do not edit by hand. Source: Memory System Specification v59; generated on 2026-10-07 -->

`Read, Add, Update, Delete`

## Rule table
### Episodic · Triggered

- 01 [Add] **Conversation events → `1_episodic/`: extract**. Write it when it happens; waiting too long is hoarding. One event per episodic, and one conversation can produce several; store a summary, not the transcript. Whether to record it at all follows the Add rules. (tools: memory_check.py)

### Semantic · Triggered

- 02 [Add] **`1_episodic/` → `2_semantic/`: extract; the only way in.** An event yields facts that carry no time; when a semantic fact changes, it is necessarily because some episodic happened.

### Procedural · Triggered

- 03 [Add] **`1_episodic/` → `3_procedural/`: count.** Compiled from repeated failures: **the same kind of error twice or more**; a one-off error goes only into `1_episodic/`.
- 04 [Add] **`2_semantic/` → `3_procedural/`: derive.** From a known fact, infer "so this is what to do". No repetition is needed, but it **must name the semantic fact it is derived from**.
- 05 [Add] **Set directly by the user → `3_procedural/`**. The user says on the spot how something should be done, and the agent records it. No repetition or derivation is needed, but **the user's exact words and the date must be quotable** (they live in the upstream episodic); if they cannot be quoted, this way in does not apply. **The exact words live only in that episodic, never in the rule file**; the rule file keeps only the action.

### Common · Boot

- 06 [Read/Add/Update/Delete] **Each thing has exactly one home and is said exactly once.** Anywhere else that needs it points to that home.
- 07 [Read/Add/Update/Delete] **Episodics are evidence, not retrieval targets**: only `Upstream` points to them, and they are browsed by time; having to browse `1_episodic/consolidated/` often means extraction was not done well. **The process stays in the episodic; upper layers keep only conclusions and inputs.** Wording that matters, such as definitions and agreements, is kept verbatim, without naming who said it.
- 08 [Read] **Memory takes priority over your own defaults**, including usage learned in training or from the literature. When a term does not fit, first check which side deviates; **if a search finds nothing, say it found nothing**, and do not fill the gap yourself. **Stopping as soon as you find something that supports what you already said is also not allowed**: you search to disprove yourself, not to reinforce yourself.
- 09 [Add/Update] **Read every line on its own once**: if it only makes sense after scrolling up or rebuilding the context, rewrite it. **Codes** (ad-hoc labels and numbers) are the most common case: use the name directly; if a number is really needed, define it in the same paragraph or the same table.
- 10 [Add/Update] **Paths**: wrap paths that currently resolve in backticks, and leave paths that do not resolve unwrapped; use angle brackets for templates and a glob for a whole batch; write paths in full, never with `../`. (tools: memory_check.py)

### Common · Triggered

- 11 [Add/Update] **A number never appears alone**: it carries its ruler (what was measured, the denominator, which span it covers, who counted it and when; if it comes from the same source as nearby numbers, write "same source"). Counts, ratios, durations, amounts, step counts, and seeds need a ruler; dates, line numbers, hashes, paths, and rule numbers do not. **A counted quantity must be able to say which ones**: give the names, or point to a list that resolves.
- 12 [Add/Update] **State the cause and effect**; do not make a claim absolute just so the sentence reads well. Every time you write "cannot", "only", or "impossible", stop and ask once: is this really absolute?
- 13 [Add/Update] Content that will be looked up goes in **tables**; content that must be understood goes in **sections**. After a label, write an **ASCII colon followed by a space** (`: `), the same as in the Summary. The tools accept both the ASCII colon and the full-width colon. (tools: tally.py, memory_check.py, gen_index.py, gen_dispatch.py)
- 14 [Add] **Private never goes to a remote; Public may.** Private files are still tracked in local git as usual; `memory_check.py` reports every Private file when the repo has a remote. (tools: memory_check.py)
- 15 [Add] **Ask two questions before keeping anything**: In what future situation will it be needed, and what cue will be used to find it then? Would deleting it cause an error, or only lose a reminder? Keep it only if both questions have answers. Ask this of every line and every section.
- 16 [Delete] **No deletion by default.** Append-only and reversible changes are made directly, then you report which files and which lines were touched; deleting, renaming, moving, or marking as obsolete always starts with a list and waits for the user to confirm (which file, how many lines, why it is obsolete, where the content still lives). The only thing that may be deleted directly is a superseded old statement in `2_semantic/`, and each deleted sentence is listed in the commit message.
- 17 [Delete] **Before anything is deleted, the original text must have a home as evidence**, pointed to in the list; "it has already been extracted" is not a reason. Retired Semantic and Procedural files move in whole into that layer's `2_semantic/history/` or `3_procedural/history/`; content cut from a rule file is written into the day's `1_episodic/`.
- 18 [Delete] **Do not decide whether to keep a file you cannot open** (PDFs, images, binaries). Say "I have not read it" first, and let the user decide.

### Semantic, Procedural · Triggered

- 19 [Update/Delete] **Before changing or deleting something, find what points to it and change those too.** When a definition changes, check downstream: `Prerequisites` depend on each other in order, so re-read every later prerequisite and every `Derived` definition to see whether it still holds; when a semantic entry changes, re-evaluate the procedurals derived from it; evidence in episodics that points to the old structure is allowed to break, and no mapping table is added for it.

### Semantic, Procedural · Boot

- 20 [Read] When you read something wrong, outdated, or duplicated, **run Update or Delete on the spot**; do not work around it.

### Semantic, Procedural · Triggered

- 21 [Add] **Upstream comes first.** Memory that cannot name its upstream is not allowed: it was made up on a hunch. (tools: memory_check.py)
- 22 [Update] **Edit in place, and only the lines that need it.** Do not write a new entry next to the old one, do not leave tombstones such as "deleted" or "moved to", and do not reorder things while you are there; how a superseded old statement is removed follows the Semantic Delete rule. **After editing**: update the Summary too (`Brief`, `Admission`, `Updated`); only on the first change to this file today, save the whole old version into that layer's `2_semantic/history/` or `3_procedural/history/` (one copy per file per day; if that name already exists, do not save again); for rule files, also run `gen_dispatch.py` and `gen_index.py`. (tools: gen_dispatch.py, gen_index.py)
- 23 [Add/Update] **A check and a semantic entry point to each other.** The check's `Upstream` names the semantic entry it is derived from, and that entry's `Before use` points back to the check. The semantic fact a check relies on is not rewritten inside the check. (tools: memory_check.py)

### Episodic · Boot

- 24 [Add] **When the sweep line is due, first write the day's episodics, and only then answer the user.** If you do not see the sweep line, run `python3 memory/tools/UserPromptSubmit/sweep_due.py` yourself; exit code 1 means it is due. Order: scan what happened in that span, one episodic per event, recording user decisions per `3_procedural/decision-attribution.md` → `python3 memory/tools/gen_index.py` → check for spec updates per `3_procedural/sweep-check-spec-updates.md` → finally stamp with `sweep_due.py --done`. The order may not be changed, and an empty day gets stamped too. (tools: sweep_due.py, gen_index.py)
- 25 [Add] **A sweep line that spans more than one day is a cold start**: write only what the evidence supports, and mark it as reconstructed from evidence. You are filling in a record, not making a judgment.

### Episodic · Triggered

- 26 [Add] **When the user makes a decision from options the agent offered**, record the options considered, the user's reasons, the assumptions relied on, and one attribution line.
- 27 [Update] **Episodics are never rewritten.** An episodic records what was true at the time, and is allowed to go out of date.
- 28 [Update] **Whether an episodic is consolidated depends on whether it has been fully extracted, not on whether the work is done.** First extract whatever the upper layers have not yet captured (thresholds per the entry rules 1–5), then move it: `python3 memory/tools/mem_mv.py 1_episodic/<file>.md 1_episodic/consolidated/<file>.md --apply`. (tools: mem_mv.py)
- 29 [Add] **Every episodic has `Errors caught by`.** Source names must match `SOURCES` in `memory/tools/tally.py` exactly; an item that does not match is not counted. `unrecorded` is not zero: it was never measured, so it is left out of the denominator. (tools: tally.py)

### Semantic · Boot

- 30 [Read] **Finding something in the semantic layer**: `Tags` and `Open when` find the file, and the heading finds the entry; read only that entry, from the top down, and stop as soon as you can answer. Read, Add, Update, and Delete all start this way.
- 31 [Read] **Before using an entry to do something**: first open the checks its `Before use` points to; do not cite anything marked `unverified` as confirmed; if the entry has a `Changes when` condition, first check whether that condition has been met.

### Semantic · Triggered

- 32 [Add/Update] **Mark only exceptions.** Reliability: a `Source` you have not verified yourself is written as `unverified`. Type: the default is fact and is not marked; a derived entry writes `Inputs`, and a judgment writes `Premises`. Invalidation: write `Changes when` only for entries that depend on a decision or external state that can change.
- 33 [Add] **Find the home before extracting**: list every file on the same topic, read from the newest, and let the newest win on conflicts; if an entry already exists, use Update instead of opening a second one; content goes into a file only if it passes that file's `Admission`, and if it does not, find its real home. **If there is no home, a file is missing**: create one, or ask the user.
- 34 [Add/Update] **The atom of semantic memory is one fact, not one file.** A file is only a container for facts that are read together and have **the same lifespan**: facts that always apply and facts that expire do not share a file.
- 35 [Add/Update] **Keep it short, and store only facts that are true now.** Semantic memory gets replaced by newer facts, so however complete the details are, they will be swapped out. Unfinished work counts too: record only that it "exists and is unresolved", and put the day it will be handled on the calendar; do not open a separate to-do list, and do not add a new layer.
- 36 [Add/Update] **The semantic layer is flat, and classification is by tag only**: many-to-many, no hierarchy among tags, used only for Semantic. The tag vocabulary is in your own `MEMORY_ARCH.md`, and each tag says "what kinds of questions route here". The `agent` tag marks the agent itself (memory system, tools, runtime environment) and never shares a file with a tag from the user's domain. (tools: memory_check.py)
- 37 [Add/Update] **Hard limits for semantic files**: at most 200 lines per file (the number is `MAX_LINES` in `memdoc.py`); beyond that, split it or trim it. Fill in every Summary field per the Summary table; entries use only the fields in the "Fields allowed under an entry" table; inside `## Memory Content`, dates are allowed only in the `Confirmed` field and in episodic paths in `Source`, because a date in a sentence is narrative; leave no empty fields: omit a field with no content entirely, and do not write "none" as a placeholder. (tools: memdoc.py, memory_check.py)

### Procedural · Boot

- 38 [Read/Update] **When you carry out a rule, record it in that episodic's `Procedurals used`**. Counts are not written in the rule file; tally accumulates them into `3_procedural/usage.json`. The condition for +1 is confirming that you actually carried the rule out, not that you read the file. (tools: tally.py)

### Procedural · Triggered

- 39 [Add/Update] **Every rule file must be reachable**: from `CLAUDE.md`, or from some semantic entry's `Before use`. The more often a rule is used, the earlier it goes. (tools: memory_check.py)
- 40 [Add] **Moving to another system**: take every rule file marked `Scope: universal`, and drop the `Upstream` field.
- 41 [Add/Update] **A rule file holds only what must be followed at the moment of acting and cannot be re-derived.** Scenario test: at the moment the action is about to happen, what do you need in front of you? Something that would not change your next action even if you knew it is not a rule; arbitrary conventions (formats, constants, thresholds) must be kept, and conclusions that can be re-derived are not kept. One rule per file, one point per line, imperative mood, no history. **Exception**: the few rules marked `Scope: this-role` that live in the boot layer are always loaded together, and splitting them would help neither finding nor counting them, so they may share one file whose `Brief` says which kind of action it covers; triggered-layer rules may not be merged, because a triggered-layer rule is found by its file name.
- 42 [Add/Update] **Examples in rule files use no project names, personal names, or private matters**; always say "the user" and "the agent". A rule that is itself about that project or role is exempt once it is marked `Scope: this-role`.
- 43 [Add] **What becomes a check**: a "check this before use" derived from a semantic fact, and a ruling the agent has made. Checks go in the triggered layer; if the agent has a systematic bias on the topic, name the bias and put it first, and mark that file `Scope: this-role`.

### Semantic, Procedural · Triggered

- 44 [Add/Update] **When to delegate to a subagent**: delegate changes that span several files, extracting new facts from raw material (transcripts, source code, literature), or reformatting a whole file (migration); appending a single entry or changing a few lines in one file you do yourself. Even when you do it yourself, review it by the rules that follow.
- 45 [Add/Update] **A subagent runs in an isolated workspace** (a git worktree) and cannot touch the current workspace; clean the workspace up as soon as its work is merged or abandoned, but never while the subagent is still running.
- 46 [Add/Update] **A subagent's report splits "things the old file did not have" into two kinds**: those forced by the format (fields and headings the new format necessarily produces) need no question; every new claim in content is **listed, and you stop to ask the user about each one**. The split is mechanical: only the fixed field positions count as format, and anything written elsewhere is a new claim. A user who has not replied yet does not block the work: put the pending items on a list, merge what has been verified, and move on to the next file.
- 47 [Add/Update] **For every semantic file a subagent changes, its report includes a "could be shortened" list** that only lists and never trims, with four things per item: which passage (a verbatim anchor, extracted with a command rather than typed by hand), how many lines, why it could be shortened, and what would be lost by shortening it.
- 48 [Add/Update] **Reviewing a change starts with four mechanical checks, the same for a subagent's output and for your own edits**, and judgment does not start until all four are done: every `-` line in the diff is accounted for in the report | each claimed source matches the original | lint and checks were run and their output is pasted | nothing in `1_episodic/consolidated/` was touched. Only then review the format item by item.
- 49 [Add/Update] **Feedback to a subagent goes only into its prompt**; while the loop runs, do not change a single character of the rule files, the spec copy, or the subagent's definition file. Give a whole section for comparison, both sides of it: "current", printed with a command and pasted, and "change to", written out as the full revised section; giving half a sentence is a violation.

### Common · Triggered

- 50 [Read/Update] **On the sweep line, check for spec updates.** Every release of the kit (`https://github.com/cxweoth/agent-memory-kit`) raises the number in its `VERSION` file by 1 and adds a `<kit>/CHANGELOG.md` entry saying which sections changed. On the sweep line, run `git pull` in your clone of the kit and compare the kit's `VERSION` with the first line of `memory/spec/VERSION`. If they differ: read every `<kit>/CHANGELOG.md` entry newer than your version and do what each entry marked **Action required** says; then rerun `gen_spec.py`, carry rule-file changes into `3_procedural/` as Add or Update per the rules, and copy the tools with `gen_spec.py --get` (review the diff before running them). The spec copy is always generated and never edited by hand; the kit does not push updates, the agent comes to read them. (tools: gen_spec.py, memory_check.py)

