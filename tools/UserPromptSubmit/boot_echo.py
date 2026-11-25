#!/usr/bin/env python3
"""On every prompt, reprint a few lines summarising boot rules into the agent's context.

Why: the boot layer is read once, at the start of a session. When a long conversation is
compacted into a summary, the summary keeps tasks and decisions but not boot rules such as
tone, how the agent refers to itself, or reply format, so the agent drifts with no signal.
Reprinting a few lines every turn survives compaction; the cost is those lines per turn.

Each agent chooses the lines: they live in `MEMORY_ARCH.md`, in the section whose heading
contains "Echo every turn", one per line. The spec only sets the cap, `MAX_LINES`; lines
past the cap are not printed, and the script says so.
The rules themselves still live in their rule files; this section holds short reminders only.

Called by `emit.py`; the output goes only into the agent's context. Prints nothing if the
section does not exist. Always exits 0.
"""
import re
from pathlib import Path

MEM = Path(__file__).resolve().parents[2]
MAX_LINES = 6


def main():
    for arch in (MEM.parent / "MEMORY_ARCH.md", MEM / "MEMORY_ARCH.md"):
        if not arch.exists():
            continue
        m = re.search(r"(?ims)^#{1,6} [^\n]*echo every turn[^\n]*$\n(.*?)(?=^#{1,6} |\Z)",
                      arch.read_text(encoding="utf-8"))
        if not m:
            continue
        lines = [l.strip() for l in m.group(1).split("\n")
                 if l.strip() and not l.strip().startswith("<!--")]   # one-line HTML comments are notes, not reminders
        if not lines:
            return
        print("Echo every turn (boot-rule reminders; the rules live in their rule files)")
        for l in lines[:MAX_LINES]:
            print("  " + l)
        if len(lines) > MAX_LINES:
            print(f"  WARNING: the section has {len(lines)} lines; only the first {MAX_LINES} are printed. Trim it to {MAX_LINES}.")
        return


try:
    main()
except Exception as e:
    print(f"WARNING: boot_echo.py failed; boot-rule reminders were not printed: {e}")
