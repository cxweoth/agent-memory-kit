# Updates and feedback

<!-- Generated file; do not edit by hand. Source: Memory System Specification v60; generated on 2026-10-07 -->

`CHANGELOG.md and GitHub Issues`

## Spec updates

- The kit at `https://github.com/cxweoth/agent-memory-kit` is the single source of truth for this spec and its tools. Every release raises the number in the kit's `VERSION` file by 1 and adds an entry to the kit's `CHANGELOG.md` listing which sections changed.
- A `CHANGELOG.md` entry is marked **Action required** when the release makes agents redo or catch up on work they have already done (a migration rule changed, a rule file was renamed, the way a tool is called changed), or when there is something that must be done that the automatic sweep-line steps would not handle. Changes to wording, merges, and added explanations get an entry without that mark.
- Agents read the changelog on the sweep line (rule `sweep-check-spec-updates.md`): only the entries newer than their own `memory/spec/VERSION`, doing what each Action-required entry says. The changelog takes no replies; to respond, open a GitHub Issue.

## What to put in an issue

| Part | What to write |
|---|---|
| Title | One sentence saying what the problem is |
| Body | What happened, what you expected, and which rule or file it concerns. **Every line self-contained** |
| From | The name of the agent opening the issue |
| Version | The spec version you are on: the first line of `memory/spec/VERSION` |

## How to open an issue

- Open a GitHub Issue at `https://github.com/cxweoth/agent-memory-kit/issues`, filled in per the table above (for example with `gh issue create --repo cxweoth/agent-memory-kit`).
- One issue per problem. Open one when the spec is **wrong, contradicts itself, is missing a rule, or has two rules that are too alike**, or when a tool does not match the spec.
- Before opening one, search the existing issues for the same problem; if it is already there, add to that issue instead of opening a new one.
- **The issue tracker is not memory**: once an issue is resolved, the conclusion goes into the spec, and the episodic about it is written by the agent that opened the issue.
