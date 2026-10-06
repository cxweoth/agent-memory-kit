#!/usr/bin/env python3
"""Scan two fields of every episodic and add them up into two tallies.

  "Procedurals used"  -> 3_procedural/usage.json        how many times each rule was used
  "Errors caught by"  -> 3_procedural/corrections.json  who caught each day's errors

Spec: counts are never written by hand; this program extracts them from the episodics.

* What matters is the **share by source, not the raw count**.
  A raw count only measures how hard the user had to work, and it drops whenever
  the user simply stays quiet. **The goal is for the share to move away from the user**
  (toward the tool, the agent itself, and other agents).
* All of these fields are filled in by the agent itself, so **the numbers are a lower
  bound, not the true value** -- the same weakness as usage.json. The "tool" column is
  harder evidence than the others, because the check output leaves an independent trace.

Usage: python3 memory/tools/tally.py
"""
import json, re, sys
from collections import Counter
from pathlib import Path

MEM = Path(__file__).resolve().parents[1]
ROOT = MEM.parents[0]
OUT = MEM / "3_procedural" / "usage.json"
OUT_C = MEM / "3_procedural" / "corrections.json"

# Who caught the error. This is the main axis: the goal is for the share to move away
# from the user.
# Each agent edits this tuple to match the error-source list in its own MEMORY_ARCH.md;
# names in the "Errors caught by" field must match these exactly.
# Missing a source here means the errors it caught silently never reach the numerator.
#   => unknown_labels() below prints any name that appears in the field but not here.
SOURCES = ("user", "tool", "self", "subagent")
# The source whose share we want to shrink; the report prints the share of everything else.
USER_SOURCE = "user"
# Longest first, so a longer name is never swallowed by a shorter one it contains.
_ALT = "|".join(re.escape(s) for s in sorted(SOURCES, key=len, reverse=True))


def corrections():
    """Scan "Errors caught by" in every episodic and add it up per day.

    Field shape: `- Errors caught by: user 2 (output corrected 2), tool 3, self 0`;
    no errors -> `none`. The note in parentheses is for humans; only SOURCES are counted.
    The day is the first YYYY-MM-DD of "Occurred"; an entry spanning days counts on its start day.
    """
    by_day, missing, blank, unknown, unparsed = {}, [], {}, {}, []
    for f in sorted((MEM / "1_episodic").rglob("*.md")):
        t = f.read_text(encoding="utf-8")
        d = re.search(r"^-\s*Occurred\s*[:：]\s*(\d{4}-\d{2}-\d{2})", t, re.M)
        m = re.search(r"^-\s*Errors caught by\s*[:：]\s*(.+?)\s*$", t, re.M)
        if not d:
            continue
        if not m:
            missing.append(f.name)
            continue
        if "unrecorded" in m.group(1).lower():
            # Backfilled old episodic: no data, so it must not be treated as zero.
            blank[d.group(1)] = blank.get(d.group(1), 0) + 1
            continue
        day = by_day.setdefault(d.group(1), dict.fromkeys(SOURCES, 0))
        hits = re.findall(r"(" + _ALT + r")\s*[xX×]?\s*(\d+)", m.group(1))
        for src, n in hits:
            day[src] += int(n)
        for lbl in _unknown_labels(m.group(1)):
            unknown.setdefault(lbl, []).append(f.name)
        # The field has text but not a single number could be read -- wrong shape,
        # so that entry's errors would never reach the numerator.
        if not hits and m.group(1).strip().lower() not in ("none", "none."):
            unparsed.append((f.name, m.group(1)[:60]))
    return by_day, missing, blank, unknown, unparsed


def _unknown_labels(field):
    """Names in the field that look like a source but are not in SOURCES.

    Shape is `<name> <number>`, segments separated by `;`, `,` (either width) or `、`.
    Notes in parentheses are ignored.
    """
    out = []
    for seg in re.split(r"[；;，,、]", re.sub(r"[（(][^）)]*[）)]", "", field)):
        m = re.match(r"\s*([^\d]+?)\s*[xX×]?\s*\d+\s*$", seg)
        if m and m.group(1) not in SOURCES:
            out.append(m.group(1))
    return out


def main():
    c = Counter()
    for f in sorted((MEM / "1_episodic").rglob("*.md")):
        m = re.search(r"^-\s*Procedurals used\s*[:：]\s*(.+?)\s*$",
                      f.read_text(encoding="utf-8"), re.M)
        if not m or m.group(1).strip().lower().startswith("none"):
            continue
        for r in re.split(r"[,，、]\s*", m.group(1)):
            # Episodics use both forms: `time-anchor` and `3_procedural/time-anchor.md`
            r = r.strip().strip("`").removesuffix(".md").rsplit("/", 1)[-1]
            if not r:
                continue
            # An episodic may name a skill (e.g. `foo`) whose file is skill_foo.md
            if not (MEM / "3_procedural" / f"{r}.md").exists() and \
               (MEM / "3_procedural" / f"skill_{r}.md").exists():
                r = f"skill_{r}"
            c[r] += 1

    known = {p.stem for p in (MEM / "3_procedural").glob("*.md")} - {"usage"}
    unknown = sorted(set(c) - known)

    OUT.write_text(json.dumps(dict(c.most_common()), ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"Scanned {len(list((MEM/'1_episodic').rglob('*.md')))} episodics")
    print(f"-> {OUT.relative_to(ROOT)}")
    for r, n in c.most_common():
        print(f"  {n:3d}  {r}")
    never = sorted(known - set(c))
    if never:
        print(f"\nNever recorded as used ({len(never)}):")
        for r in never:
            print(f"    {r}")
    if unknown:
        print(f"\n⚠️ Named in episodics but missing from 3_procedural/: {', '.join(unknown)}")

    by_day, missing, blank, unknown, unparsed = corrections()
    OUT_C.write_text(json.dumps(by_day, ensure_ascii=False, indent=1, sort_keys=True),
                     encoding="utf-8")
    print(f"\nErrors caught by -> {OUT_C.relative_to(ROOT)}")
    if by_day:
        # Column widths follow SOURCES, so adding a source needs no change to the printer.
        w = [max(len(s) + 2, 6) for s in SOURCES]
        head = "".join(f"{s:>{n}}" for s, n in zip(SOURCES, w))
        print(f"  {'Date':<10}{head}   not-{USER_SOURCE} share")
        tot = dict.fromkeys(SOURCES, 0)
        for day in sorted(by_day):
            k = by_day[day]
            n = sum(k.values())
            share = f"{(n - k.get(USER_SOURCE, 0)) / n:.0%}" if n else "—"
            for x in SOURCES:
                tot[x] += k[x]
            row = "".join(f"{k[s]:>{n2}d}" for s, n2 in zip(SOURCES, w))
            print(f"  {day}{row}   {share:>8}")
        n = sum(tot.values())
        share = f"{(n - tot.get(USER_SOURCE, 0)) / n:.0%}" if n else "—"
        row = "".join(f"{tot[s]:>{n2}d}" for s, n2 in zip(SOURCES, w))
        print(f"  {'Total':<10}{row}   {share:>8}")
        print(f"  * The goal is for the not-{USER_SOURCE} share to go up. "
              f"The raw count is not the metric.")
        if blank:
            tot_b = sum(blank.values())
            print(f"  ⚠️ Another {tot_b} entries are marked `unrecorded` (field was backfilled; "
                  f"nothing was measured then). **Not zero, and not in the denominator.**")
    else:
        print("  No episodic has this field yet")
    if unknown:
        print(f"\n⚠️ {len(unknown)} source name(s) appear in the field but not in SOURCES"
              f" (the errors they caught are not in the numerator):")
        for lbl, files in sorted(unknown.items()):
            print(f"    {lbl}  ({len(files)} entries, e.g. {files[0]})")
    if unparsed:
        print(f"\n⚠️ {len(unparsed)} entries have text in \"Errors caught by\" but in a shape "
              f"no number could be read from (expected `user 3, tool 0, self 2`):")
        for n, s in unparsed:
            print(f"    {n}\n        {s}…")
    if missing:
        print(f"\n⚠️ {len(missing)} entries lack the \"Errors caught by\" field:")
        for n in missing:
            print(f"    {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
