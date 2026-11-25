#!/usr/bin/env python3
"""Print the agent's own to-dos that have come due: things it promised, that cost only its own time, and have a due date.

The rule is `3_procedural/promises-go-in-the-due-list.md`. Called by `emit.py` on every prompt;
the output goes only into the agent's context, not onto the user's screen.

Why this file exists: an agent says "I'll do it Monday" or "I'll add it before the sweep line",
and the next session cold-starts from files and does not remember the promise. Written to a
file, the promise surfaces by itself when due; `source` tells the cold-started agent why.
Anything that costs the user's time, or needs the user's decision, does not go here: that
belongs on the calendar.

File `memory/due.json`: one array, one row per item.
  {"due": "2026-11-30 17:30", "what": "...", "source": "1_episodic/<file>.md"}
  `due` is local time; a bare date is allowed (taken as 00:00 that day).

Usage:
  python3 memory/tools/UserPromptSubmit/due.py                  print what is due; print nothing if none
  python3 memory/tools/UserPromptSubmit/due.py --all            list everything, numbered
  python3 memory/tools/UserPromptSubmit/due.py --add "<due>" "<what>" ["<source>"]
  python3 memory/tools/UserPromptSubmit/due.py --done <number>  delete that row (numbers as in --all)
  Always exits 0: it is part of the hook, and a failure must not block the user's prompt.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

DUE = Path(__file__).resolve().parents[2] / "due.json"


def when(s):
    s = str(s).strip().replace("T", " ")
    for fmt, n in (("%Y-%m-%d %H:%M", 16), ("%Y-%m-%d", 10)):
        try:
            return datetime.strptime(s[:n], fmt)
        except ValueError:
            pass
    return None


def load():
    if not DUE.exists():
        return []
    rows = json.loads(DUE.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("the top level must be an array")
    return rows


def save(rows):
    DUE.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def line(i, r):
    src = f"  source: {r['source']}" if r.get("source") else "  WARNING: no source"
    return f"  {i}. {r.get('due', '?')}  {r.get('what', '?')}{src}"


def main():
    a = sys.argv[1:]
    if "-h" in a or "--help" in a:
        print(__doc__)
        return
    rows = load()
    if a[:1] == ["--add"]:
        if len(a) < 3 or when(a[1]) is None:
            print('usage: due.py --add "<YYYY-MM-DD[ HH:MM]>" "<what>" ["<source>"]')
            return
        row = {"due": a[1], "what": a[2]}
        if len(a) > 3:
            row["source"] = a[3]
        rows.append(row)
        rows.sort(key=lambda r: when(r.get("due", "")) or datetime.max)
        save(rows)
        print(f"recorded; {len(rows)} item(s) now")
        return
    if a[:1] == ["--done"]:
        try:
            n = int(a[1])
            if n < 1:
                raise IndexError
            gone = rows.pop(n - 1)
        except (IndexError, ValueError):
            print("no such number; run --all to see the numbers")
            return
        save(rows)
        print(f"deleted: {gone.get('what', '?')} ({len(rows)} left)")
        return
    if "--all" in a:
        print(f"due list: {len(rows)} item(s)")
        for i, r in enumerate(rows, 1):
            print(line(i, r))
        return
    now = datetime.now()
    bad = [i for i, r in enumerate(rows, 1) if when(r.get("due", "")) is None]
    hit = [(i, r) for i, r in enumerate(rows, 1)
           if (when(r.get("due", "")) or datetime.max) <= now]
    if hit:
        print(f"DUE: {len(hit)} of your own to-do(s) (when done: due.py --done <number>)")
        for i, r in hit:
            print(line(i, r))
    if bad:
        print(f"WARNING: memory/due.json row(s) {bad} have an unreadable `due` and will never surface")


try:
    main()
except Exception as e:                      # part of the hook: say so, do not block
    print(f"WARNING: due.py failed; due to-dos were not checked: {e}")
