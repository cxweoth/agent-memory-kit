# delegating-memory-edits

## Memory Summary
- Visibility: Public
- Brief: When to delegate an Add or Update of memory to a subagent, and how: isolated workspace, report categories, review, feedback
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-09-20

## Memory Content

- **When to delegate to a subagent**: delegate changes that span several files, extracting new facts from raw material (transcripts, source code, literature), or reformatting a whole file (migration); appending a single entry or changing a few lines in one file you do yourself. Even when you do it yourself, review it by the rules that follow.
- **A subagent runs in an isolated workspace** (a git worktree) and cannot touch the current workspace; clean the workspace up as soon as its work is merged or abandoned, but never while the subagent is still running.
- **A subagent's report splits "things the old file did not have" into two kinds**: those forced by the format (fields and headings the new format necessarily produces) need no question; every new claim in content is **listed, and you stop to ask the user about each one**. The split is mechanical: only the fixed field positions count as format, and anything written elsewhere is a new claim. A user who has not replied yet does not block the work: put the pending items on a list, merge what has been verified, and move on to the next file.
- **For every semantic file a subagent changes, its report includes a "could be shortened" list** that only lists and never trims, with four things per item: which passage (a verbatim anchor, extracted with a command rather than typed by hand), how many lines, why it could be shortened, and what would be lost by shortening it.
- **Reviewing a change starts with four mechanical checks, the same for a subagent's output and for your own edits**, and judgment does not start until all four are done: every `-` line in the diff is accounted for in the report | each claimed source matches the original | lint and checks were run and their output is pasted | nothing in `1_episodic/consolidated/` was touched. Only then review the format item by item.
- **Feedback to a subagent goes only into its prompt**; while the loop runs, do not change a single character of the rule files, the spec copy, or the subagent's definition file. Give a whole section for comparison, both sides of it: "current", printed with a command and pasted, and "change to", written out as the full revised section; giving half a sentence is a violation.
