# agent-memory-kit

A memory system that an AI agent builds and maintains for itself: a written spec, plus plain-Python tools that check the agent follows it.

The agent owns the memory. It records what happened (**episodic**), extracts facts that stay true (**semantic**), and compiles how to do things (**procedural**) from repeated mistakes, from facts, or from what the user tells it directly. Everything is Markdown files in git, so the user can read, diff and roll back anything the agent remembers.

```
memory/
├── 1_episodic/      what happened, one file per event, never rewritten
│   └── consolidated/  episodics whose facts have been extracted
├── 2_semantic/      facts that are true now, found by tag and entry heading
├── 3_procedural/    rules: boot layer (always loaded) and triggered layer
├── spec/            generated copy of this spec
└── tools/           the scripts below
```

## For agents: set up your memory

You only need this repo. Read the spec, then install.

1. **Read the spec**, in order: [`spec/md/`](spec/md/) sections 00–09. [`spec/md/BOOT.md`](spec/md/BOOT.md) holds the rules you load at the start of every conversation; [`spec/md/rules/`](spec/md/rules/) holds every rule file.
2. **Install** into your project root (the folder holding your `CLAUDE.md`):
   ```sh
   git clone https://github.com/cxweoth/agent-memory-kit.git ~/agent-memory-kit
   python3 ~/agent-memory-kit/install.py /path/to/agent --agent <your name> --user <user's name> --hook
   ```
   It creates `memory/`, copies the tools, generates `memory/spec/`, imports the universal rule files into `memory/3_procedural/` with an import episodic as their `Upstream`, writes `MEMORY_ARCH.md`, adds a Memory section to `CLAUDE.md`, and (with `--hook`) registers the `UserPromptSubmit` hook in `.claude/settings.json`. Re-running it never overwrites existing files.
3. **Fill in `MEMORY_ARCH.md`**: your tags and error sources. Keep `SOURCES` in `memory/tools/tally.py` identical to the error-source list.
4. **Check**: `python3 memory/tools/memory_check.py`.
5. **Stay current**: on every sweep line, follow `sweep-check-spec-updates.md` (pull this repo, compare `VERSION`, read `CHANGELOG.md`).

Requirements: Python 3.9+, git. No third-party packages. The hook is written for Claude Code; the rest works with any agent that can read files and run Python.

## Tools

| Script | What it does |
|---|---|
| `memory_check.py` | Checks the whole memory: Summary fields, upstream pointers, tags, reachability of every rule file, dead paths, file size |
| `memdoc.py` | Parses and lints semantic files; `--selftest` |
| `tally.py` | Counts which rules were used and who caught errors, from episodics |
| `gen_index.py` | Generates `INDEX.md` from every file's Summary |
| `gen_dispatch.py` | Copies each rule file's Brief into the dispatch table in `CLAUDE.md` |
| `gen_spec.py` | Generates the spec copy from `spec/spec.json`; `--get` copies the kit's tools |
| `mem_mv.py` | Moves a memory file and updates what points to it |
| `mem_recall.py` | Lists semantic files and unconsolidated episodics for each prompt |
| `UserPromptSubmit/` | Hook: current time, sweep-line check, reply checks |

Full descriptions: [`spec/md/08_Tools.md`](spec/md/08_Tools.md).

## Repository layout

| Path | What |
|---|---|
| `spec/spec.json` | The spec. The single source; everything in `spec/md/` is generated from it |
| `spec/md/` | Readable rendering, regenerate with `python3 tools/gen_spec.py spec/spec.json spec/md` |
| `tools/` | The tools, copied into each agent's `memory/tools/` |
| `templates/` | `CLAUDE.md` section, `MEMORY_ARCH.md`, hook settings |
| `install.py` | First-time setup |
| `VERSION`, `CHANGELOG.md` | Spec version and what changed |

## Feedback

Found a rule that is wrong, contradictory, missing, or two rules that overlap, or a tool that disagrees with the spec? [Open an issue](https://github.com/cxweoth/agent-memory-kit/issues). Section 09 of the spec says what to put in it.

## License

MIT
