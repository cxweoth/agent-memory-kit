#!/usr/bin/env python3
"""Put "what to look up" in front of the agent, without asking it to decide first.

The recall loop:
  read the user's message -> look at this list -> pick what may be relevant
  -> open those files for detail -> only then answer

* Why not pick tags first and then look up: the typical failure is not a bad lookup
  but the agent **never entering the decision at all**. So by default this lists
  everything and takes the decision out of the lookup. The semantic layer is small
  enough that listing it all costs less than deciding.

* Only semantic memory is listed, not procedural: rules are surfaced through `Access`
  (the boot layer is always loaded, the triggered layer by situation), not this path.

* Unconsolidated episodics are always listed: their facts **have not reached the
  semantic layer yet**, so no tag finds them, yet the answer may be in them.
  Consolidated ones are not listed; the semantic layer already covers them.

Usage:
  python3 memory/tools/mem_recall.py                    list everything
  python3 memory/tools/mem_recall.py <tag> [<tag>...]   only files tagged with any of these
  python3 memory/tools/mem_recall.py --unconsolidated   only the unconsolidated episodics
  python3 memory/tools/mem_recall.py --semantic         only semantic files, skip the episodic part
  python3 memory/tools/mem_recall.py --brief            also print each unconsolidated episodic's Brief

* `--unconsolidated` and `--semantic` can back slash commands of the same name.
  Calling it **with no arguments is reserved for the per-prompt hook** (emit.py): that
  path needs to see the unconsolidated episodics; `--semantic` does not. Each use gets
  its own flag. **The definition of "unconsolidated" lives only in `unconsolidated()`
  below**; anything else that needs it should call it rather than glob on its own --
  that would add a second place that can disagree.
"""
import re
import sys
from pathlib import Path

MEM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_tags():
    """Tag vocabulary from this agent's MEMORY_ARCH.md (same reader as memory_check.py).
    None when not defined; then any tag is accepted."""
    try:
        from memory_check import load_tags as _load
        return _load()
    except Exception:
        return None


TAGS = load_tags()


def summary(p):
    """The `## Memory Summary` fields as a dict. Accepts both ':' and '：' after labels."""
    t = p.read_text(encoding="utf-8")
    m = re.search(r"^## Memory Summary[ \t]*$\n(.*?)(?=^## |\Z)", t, re.S | re.M)
    return dict(re.findall(r"^-\s*(\S.*?)\s*[:：]\s*(.+?)\s*$", m.group(1), re.M)) if m else {}


def cut(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def unconsolidated(width=44, note="", brief=True):
    """Episodics directly under `1_episodic/`, not yet moved into `consolidated/`.
    Prints the count, then one per line.

    `brief=False` prints file names only, without the Brief: for the hook that runs on
    every prompt, to save tokens. File names are still one per line, so a count is
    always followed by which ones it is.
    """
    eps = sorted((MEM / "1_episodic").glob("*.md"))
    print(f"Unconsolidated episodics: {len(eps)}{note}")
    for p in eps:
        if brief:
            print(f"  {p.name:<40}  {cut(summary(p).get('Brief', ''), width)}")
        else:
            print(f"  {p.name}")
    return len(eps)


def main():
    if "--unconsolidated" in sys.argv[1:]:
        unconsolidated(width=72)
        return 0
    want = {a.strip().lower() for a in sys.argv[1:] if not a.startswith("-")}
    if TAGS and want - TAGS:
        print(f"❌ Unknown tag(s): {sorted(want - TAGS)}; available: {sorted(TAGS)}")
        return 2

    rows = []
    for p in sorted((MEM / "2_semantic").glob("*.md")):
        d = summary(p)
        tags = {t.strip() for t in re.split(r"[,，、]", d.get("Tags", "")) if t.strip()}
        if want and not (tags & want):
            continue
        rows.append((f"2_semantic/{p.name}", ",".join(sorted(tags)),
                     d.get("Open when", d.get("Brief", ""))))

    print(f"Semantic memory: {len(rows)}" + (f" (tags: {' '.join(sorted(want))})" if want else ""))
    w = max((len(r[0]) for r in rows), default=0)
    for path, tags, when in rows:
        print(f"  {path:<{w}}  {tags:<22}  <- {cut(when, 44)}")

    if "--semantic" not in sys.argv[1:]:
        print()
        brief = "--brief" in sys.argv[1:]
        unconsolidated(note=" (untagged, always listed; their facts are not in the semantic layer yet)"
                       + ("" if brief else ". For Briefs run with --unconsolidated"), brief=brief)
    return 0


if __name__ == "__main__":
    sys.exit(main())
