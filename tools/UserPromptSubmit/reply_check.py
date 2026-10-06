#!/usr/bin/env python3
"""Measure the shape of the previous reply. Prints only, never judges.

The problem it addresses: limits on reply shape (how many status icons, a fixed
Check / Conclusion skeleton) were only ever noticed when the user pointed them out on
the spot. Injecting the rule text into context does not make it followed; measuring does.

* Why it hangs on UserPromptSubmit rather than Stop: it looks at the *previous* reply,
  which is already in the transcript by the time the next prompt arrives, so no extra
  hook event is needed.

⚠️ Prints numbers only: never judges, never blocks, always exits 0. Once a metric
becomes a score it stops being a metric -- what gets optimized is how things are recorded.

⚠️ It reads the Claude Code transcript, not memory files, so it does not break the
rule that hooks do not read memory file contents.
"""
import json, re, sys
from pathlib import Path

# Status icons counted against the limit. A doubled icon counts twice.
# Edit both to match your own reply-shape rule.
ICONS = "🔴⭐⚠️✅❌❓⏳⏱️🔥💡📬"
ICON_LIMIT = 3
# Reply skeleton: if both markers appear, a `---` line must separate them.
CHECK_MARK, CONCLUSION_MARK = "**Check**", "**Conclusion**"
# A reply longer than this with zero reads in its turn gets flagged.
# Short planning replies stay below it, so the line does not become per-turn noise.
LONG_REPLY_CHARS = 800


def transcript():
    """The newest .jsonl in the projects directory for this cwd."""
    # Claude Code replaces every non-alphanumeric character of the cwd with `-`.
    # Paths may contain spaces, `@`, `.`, `_` and more, so use a regex, not single replaces.
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    d = Path.home() / ".claude" / "projects" / slug
    if not d.is_dir():
        return None
    js = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return js[0] if js else None


# Tools that count as "looked something up". Mechanical criterion: did this call bring
# data back from outside.
# ⚠️ Writes do not count (Write, Edit, write_db, SendMessage): writing is not looking up.
READ_TOOLS = {"Read", "Grep", "Glob", "Bash", "WebFetch", "WebSearch",
              "ListAgents", "Task", "Agent", "NotebookRead"}
READ_ACTIONS = {"read_db", "read", "list", "comments", "list_files", "read_file",
                "list_assets", "read_asset", "status"}


def previous_reply(p):
    """Return (text of the previous reply, number of reads in that turn).

    A turn = from the last user message up to this text. Only tool_use blocks in that
    span are counted, so lookups from earlier turns do not count -- what this guards
    against is passing off old data as current.
    """
    last, reads = "", 0
    with p.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") == "user":
                reads = 0          # a new turn starts; count again
                continue
            if d.get("type") != "assistant":
                continue
            c = d.get("message", {}).get("content", [])
            for b in c:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name = b.get("name", "")
                if name in READ_TOOLS:
                    reads += 1
                elif name == "Artifact":
                    if (b.get("input") or {}).get("action") in READ_ACTIONS:
                        reads += 1
                elif name.startswith("mcp__"):
                    # Connectors: names starting with get / list / search / read / find /
                    # fetch count as lookups; everything else counts as a write.
                    tail = name.rsplit("__", 1)[-1].lower()
                    if tail.startswith(("get", "list", "search", "read", "find", "fetch")):
                        reads += 1
            t = "".join(b.get("text", "") for b in c
                        if isinstance(b, dict) and b.get("type") == "text")
            if t.strip():
                last = t
    return last, reads


def main():
    p = transcript()
    if not p:
        return
    t, reads = previous_reply(p)
    if not t:
        return
    # Count each icon code point once; skip the U+FE0F variation selector, which
    # several icons share and would otherwise be counted again.
    n = sum(t.count(ch) for ch in set(ICONS) - {"\ufe0f"})
    issues = []
    if n > ICON_LIMIT:
        issues.append(f"icons {n} (limit {ICON_LIMIT})")
    if CHECK_MARK in t and CONCLUSION_MARK in t:
        head = t.split(CONCLUSION_MARK, 1)[0]
        if "\n---\n" not in head:
            issues.append("missing --- between Check and Conclusion")
    # "Look it up before stating live status" has no other mechanism.
    # ⚠️ This only catches "answered without looking at all", not "looked halfway" --
    # reading only the first message of a thread counts as having looked.
    if reads == 0 and len(t) > LONG_REPLY_CHARS:
        issues.append("zero reads last turn, yet the reply is long")
    print("🪞 Previous reply: " + (" | ".join(issues) if issues else f"icons {n}, skeleton OK"))


try:
    main()
except Exception:
    pass
