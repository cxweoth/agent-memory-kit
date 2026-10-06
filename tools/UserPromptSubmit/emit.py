#!/usr/bin/env python3
"""Send the output of the scripts below into both the agent's context and the user's screen.

Claude Code does not show a UserPromptSubmit hook's plain stdout to the user
(official docs: a successful hook's stdout is never shown in the transcript).
Only the JSON `systemMessage` is shown, so the same text goes out both ways.
Called by the UserPromptSubmit hook in .claude/settings.json; always exits 0.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Shown to the user and to the agent: the short lines. Order is the display order.
SCRIPTS = ("now.py", "sweep_due.py", "reply_check.py")
# Agent only: the recall list (can be long), kept off the user's screen.
RECALL = "../mem_recall.py"


def run(name, *args):
    if not (HERE / name).resolve().exists():   # script not installed here -> skip it
        return ""
    p = subprocess.run([sys.executable, str(HERE / name), *args],
                       capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


def main():
    recall = ""
    try:
        body = "\n".join(x for x in (run(s) for s in SCRIPTS) if x)
        recall = run(RECALL)
    except Exception as e:
        body = f"⚠️ emit.py failed; time and sweep line were not checked: {e}"
    if not body:
        body = "⚠️ now.py and sweep_due.py produced no output"
    print(json.dumps(
        {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                "additionalContext": body + ("\n\n" + recall if recall else "")},
         "systemMessage": body},
        ensure_ascii=False))


main()
