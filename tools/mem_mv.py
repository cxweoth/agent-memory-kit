#!/usr/bin/env python3
"""Move or rename one memory file, and rewrite every path that points to it.

Three operations share one shape, and all use this tool:
  consolidate  1_episodic/x.md       -> 1_episodic/consolidated/x.md
  rename       2_semantic/self.md    -> 2_semantic/capacity.md
  retire       2_semantic/x.md       -> 2_semantic/history/x_YYYY-MM-DD.md

* It is the only program allowed to rewrite memory files, and it may only change path
  strings, **never content**. **Pointers inside 1_episodic/ and history/ are never
  changed**: those are records, and if they point at an old layout, let them break.
  Three conditions, none optional:
  1. dry-run by default; only `--apply` changes anything
  2. print every changed line, before and after
  3. **after it runs, the agent must verify on its own**; the script's self-check does not count

Usage:
  python3 memory/tools/mem_mv.py <old path> <new path>           print only
  python3 memory/tools/mem_mv.py <old path> <new path> --apply   actually move

Paths are relative to `memory/`, e.g. `1_episodic/x.md`.
"""
import re
import subprocess
import sys
from pathlib import Path

MEM = Path(__file__).resolve().parents[1]
ROOT = MEM.parents[0]        # the repo root; upper bound of the search in refs()
SKIP = {"INDEX.md"}          # generated; rewritten by gen_index.py


# Records are not rewritten: 1_episodic/ (including consolidated/) and the history/ of
# both layers. Episodics are never rewritten, and a record pointing at an old layout is
# left to break rather than patched with a mapping table. Also, `Procedurals used` is
# input to tally.py: pointing it at history/ would count a retired rule file as used.
FROZEN = ("1_episodic/", "/history/")


def frozen(p: Path) -> bool:
    rel = p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
    return any(f in rel for f in FROZEN)


def refs(old):
    """Find every place that points to old. Returns
    ([(file, line no, line)] to change, [(file, line no, line)] in records, left alone)."""
    out, keep = [], []
    for p in sorted(ROOT.rglob("*.md")):
        if ".git/" in str(p) or p.name in SKIP:
            continue
        try:
            lines = p.read_text(encoding="utf-8").split("\n")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            if old in line:
                (keep if frozen(p) else out).append((p, i, line))
    return out, keep


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    old, new = sys.argv[1], sys.argv[2]
    apply = "--apply" in sys.argv
    src, dst = MEM / old, MEM / new

    if not src.exists():
        print(f"❌ Source does not exist: {old}")
        return 1
    if dst.exists():
        print(f"❌ Target already exists, not overwriting: {new}")
        return 1

    found, kept = refs(old)
    print(f"{'[APPLY]' if apply else '[dry-run, print only]'} {old} -> {new}")
    print(f"{len(found)} reference(s) will change"
          f" (`INDEX.md` excluded; gen_index.py rewrites it):\n")
    for p, i, line in found:
        rel = p.relative_to(ROOT)
        print(f"  {rel}:{i}")
        print(f"    - {line.strip()[:100]}")
        print(f"    + {line.replace(old, new).strip()[:100]}")
    if kept:
        print(f"\n{len(kept)} reference(s) in records left unchanged, let them break"
              f" (1_episodic/ and history/ are not rewritten):")
        for p, i, line in kept:
            print(f"  {p.relative_to(ROOT)}:{i}    {line.strip()[:80]}")

    if not apply:
        print(f"\nAdd --apply to actually move.")
        return 0

    for p, _, _ in {(p, 0, 0) for p, _, _ in found}:
        t = p.read_text(encoding="utf-8")
        p.write_text(t.replace(old, new), encoding="utf-8")
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    print(f"\n✅ Changed {len(found)} reference(s) in {len({p for p, _, _ in found})} file(s); "
          f"file moved to {new}")

    subprocess.run([sys.executable, str(MEM / "tools" / "gen_index.py")], cwd=ROOT)
    print("\n⚠️ The script stops here. **The agent must verify on its own**; "
          "these two are not the script's job:")
    print("   1. python3 memory/tools/memory_check.py   (Upstream and in-body pointers)")
    print(f"   2. search the whole repo for leftovers: make sure nothing still says {old}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
