#!/usr/bin/env python3
"""Check the `## Memory Summary` of every memory file under memory/, plus repo-wide memory health.

Why it exists: a file declared private can quietly end up tracked by git and pushed.
When the declaration and the actual state live in different places, they drift apart
independently. This check lines the two up.

Layout assumed: <agent root>/memory/tools/memory_check.py, with MEMORY_ARCH.md and
CLAUDE.md in the agent root (MEMORY_ARCH.md may also live in memory/). The agent root
may be a subdirectory of a git repo.

Spec: the memory system spec (local copy in `memory/spec/`); the Tags vocabulary is read
from this agent's `MEMORY_ARCH.md`.

Usage:
  python3 memory/tools/memory_check.py            run every check
  python3 memory/tools/memory_check.py --format   also print every semantic-format problem in detail
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

MEM = Path(__file__).resolve().parents[1]   # memory/
ROOT = MEM.parents[0]                       # agent root (where MEMORY_ARCH.md and CLAUDE.md live)

USAGE = __doc__


def git_top() -> Path:
    """Repo root. The agent root may be a subdirectory of the repo (<repo>/agent/memory/); paths relative to the repo root also count."""
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, capture_output=True, text=True)
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else ROOT


TOP = git_top()
BASES = (MEM, ROOT, TOP)       # pointers are looked up in these three places; reported only if none has them

# The three kinds of memory have different fields, deliberately.
LAYERS = {"episodic": "1_episodic", "semantic": "2_semantic", "procedural": "3_procedural"}
FIELDS = {
    "episodic": ["Visibility", "Brief", "Occurred", "Transcript", "Procedurals used", "Errors caught by"],
    "semantic": ["Visibility", "Tags", "Brief", "Admission", "Open when", "Upstream", "Updated"],
    "procedural": ["Visibility", "Brief", "Upstream", "Access", "Scope", "Updated"],
}
VISIBILITY = {"Private", "Public"}
# Scope: who does this rule belong to? If a different agent took over the same person's work, would it still apply?
# universal = yes (any agent) | this-user = yes (any agent serving the same person) | this-role = no (tied to the job)
SCOPE = {"universal", "this-user", "this-role"}
# A rule declared `Scope: universal` must not contain these words: refer to people as "the user"
# and "the agent", and do not use project names in examples (rule-files-hold-only-rules.md).
# Fill in your own names (people, agents, projects); empty means the check is off.
NOT_PORTABLE: tuple = ()

_SUMMARY = re.compile(r"^## Memory Summary[ \t]*$\n(.*?)(?=^## |\Z)", re.S | re.M)
_FIELD = re.compile(r"^-\s*(\S.*?)\s*[:：]\s*(.+?)\s*$", re.M)


def load_tags():
    """The Tags vocabulary lives in this agent's MEMORY_ARCH.md, not hard-coded here.

    Two forms are accepted under a heading containing "Tag": the first cell of each
    table row, or a `- tag: description` list. Returns None if nothing is found; the
    caller then reports "vocabulary not defined" once instead of flagging every tag.
    """
    for arch in (ROOT / "MEMORY_ARCH.md", MEM / "MEMORY_ARCH.md"):
        if not arch.exists():
            continue
        text = arch.read_text(encoding="utf-8")
        m = re.search(r"(?ms)^#{1,6} [^\n]*[Tt]ag[^\n]*$\n(.*?)(?=^#{1,6} |\Z)", text)
        if not m:
            continue
        tags = set()
        for line in m.group(1).split("\n"):
            line = line.strip()
            cell = None
            if line.startswith("|"):
                cell = line.strip("|").split("|")[0]
                if set(cell.strip()) <= set("-: ") or cell.strip().lower() in ("tag", "tags", "value", "name"):
                    continue
            elif re.match(r"^[-*]\s*\S", line):
                cell = re.split(r"[:：]", line.lstrip("-* "), maxsplit=1)[0]
            if cell:
                cell = cell.strip().strip("`").strip()
                if cell and " " not in cell:
                    tags.add(cell)
        if tags:
            return tags
    return None


def kind(rel: str):
    for k, d in LAYERS.items():
        if f"/{d}/" in rel:
            return k
    return None


def is_repo() -> bool:
    """Is ROOT inside a git work tree?

    Why ask: outside a repo `git check-ignore` fails fatally every time, and a fatal
    exit code is non-zero, which ignored() would read as "not ignored". Every file
    declared Private would then be a false alarm. Skip the whole check instead of
    treating a failure as an answer.
    """
    return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                          cwd=ROOT, capture_output=True).returncode == 0


def has_remote() -> bool:
    """Does this repo have a remote configured?

    Why ask: Private means "never pushed to a remote", not "never in git". Without a
    remote, tracking a Private file locally leaks nothing; the moment someone adds a
    remote, this check lights up every tracked Private file. That is the gate.
    """
    return bool(subprocess.run(["git", "remote"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip())


def skip_ptr(m: str) -> bool:
    """Should this pointer be skipped? Templates (containing < or *) and home-relative paths cannot be verified."""
    return "<" in m or "*" in m or m.startswith("~/")


def ignored(path: Path) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", str(path)],
                          cwd=ROOT).returncode == 0


def summary_of(text: str) -> dict:
    m = _SUMMARY.search(text)
    return dict(_FIELD.findall(m.group(1))) if m else {}


def before_use(text: str) -> str:
    """The `Before use` lines of a semantic file."""
    return "\n".join(re.findall(r"(?m)^.*Before use.*$", text))


def main() -> int:
    if "-h" in sys.argv or "--help" in sys.argv:
        print(USAGE)
        return 0
    problems, checked = [], 0
    tags = load_tags()
    if tags is None:
        problems.append("Tags vocabulary not defined: MEMORY_ARCH.md has no Tag section "
                        "(first cell of each table row, or `- tag: description`); the per-file tag check is skipped")
    repo = is_repo()
    remote = repo and has_remote()
    for f in sorted(MEM.rglob("*.md")):
        rel = str(f.relative_to(ROOT))
        if "/history/" in rel or "/tools/" in rel:
            continue
        k = kind(rel)
        if not k:
            continue
        checked += 1
        text = f.read_text(encoding="utf-8")
        s = summary_of(text)
        if not s:
            problems.append(f"no `## Memory Summary`          {rel}")
            continue
        for field in FIELDS[k]:
            if field not in s:
                problems.append(f"[{k}] missing field '{field}'     {rel}")
        vis = s.get("Visibility", "").strip()
        if vis and vis not in VISIBILITY:
            problems.append(f"Visibility '{vis}' is not Private/Public   {rel}")
        elif remote and vis == "Private" and not ignored(f):
            problems.append(f"declared Private but would be pushed to the remote   {rel}")
        elif repo and vis == "Public" and ignored(f):
            problems.append(f"declared Public but gitignored   {rel}")
        scope = s.get("Scope", "").strip()
        if scope and scope not in SCOPE:
            problems.append(f"Scope '{scope}' is not one of universal/this-user/this-role   {rel}")
        # A rule declared universal must actually be portable: no names specific to this setup.
        # `Upstream` is the only exempt field; it naturally points at this agent's own episodics.
        # Only 3_procedural/ files that explicitly say `Scope: universal`. Episodics record what
        # happened that day and naturally contain project and person names.
        if k == "procedural" and scope == "universal" and NOT_PORTABLE:
            txt = "\n".join(l for l in text.splitlines()
                             if not re.match(r"^-\s*Upstream\s*[:：]", l))
            hit = sorted({w for w in NOT_PORTABLE if w in txt})
            if hit:
                problems.append(f"Scope universal but contains {hit}   {rel}")
        for t in re.split(r"[,，]\s*", s.get("Tags", "")):
            t = t.strip().strip("`")
            if tags is not None and t and t not in tags:
                problems.append(f"tag '{t}' is not in the MEMORY_ARCH.md vocabulary   {rel}")
        # Files named in `Upstream` must exist. Pointers in the body are not checked here (too many false positives).
        for p in re.findall(r"[\w./-]+\.md", s.get("Upstream", "")):
            if not any((base / p).exists() for base in (MEM, f.parent, ROOT, TOP)):
                problems.append(f"Upstream not found: {p}   {rel}")

    # Extra health signals (not errors).
    times = []
    for e in sorted((MEM / "1_episodic").rglob("*.md")):
        m = re.search(r"^-\s*Occurred\s*[:：]\s*(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}):(\d{2}))?",
                      e.read_text(encoding="utf-8"), re.M)
        if m:
            times.append(datetime.datetime(int(m[1][:4]), int(m[1][5:7]), int(m[1][8:10]),
                                           int(m[2] or 0), int(m[3] or 0)))
    semantic_files = sorted((MEM / "2_semantic").glob("*.md"))
    tagcount = []
    for f in semantic_files:
        d = summary_of(f.read_text(encoding="utf-8"))
        if d.get("Tags"):
            tagcount.append(len(re.split(r"[,，]", d["Tags"])))

    # Semantic file format. The format knowledge lives only in memdoc; this just calls it.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import memdoc
    fmt = []
    for f in semantic_files:
        bad = memdoc.lint_semantic(memdoc.MemDoc(f.read_text(encoding="utf-8"), f))
        if bad:
            fmt.append((len(bad), f.name, bad))

    # Subagent worktrees left behind. Relying on someone remembering to clean them up fails, so print them.
    wt = []
    if repo:
        out = subprocess.run(["git", "worktree", "list", "--porcelain"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        for line in out.split("\n"):
            if line.startswith("worktree ") and ".claude/worktrees" in line:
                wt.append(line[len("worktree "):])

    # Every rule file must be reachable, by one of two routes: from CLAUDE.md, or from the
    # `Before use` of some semantic entry. Reachable by neither means it is an orphan.
    claude_md = ROOT / "CLAUDE.md"
    claude = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    semantic = {f.name: f.read_text(encoding="utf-8") for f in semantic_files}
    procedural = {f.name: f.read_text(encoding="utf-8") for f in sorted((MEM / "3_procedural").glob("*.md"))}
    for name, ptext in procedural.items():
        from_claude = f"3_procedural/{name}" in claude
        pointed_by = [sn for sn, st in semantic.items() if name in before_use(st)]
        if not from_claude and not pointed_by:
            problems.append(f"orphan rule: neither CLAUDE.md nor any entry's `Before use` points to it   memory/3_procedural/{name}")
        # A check and its semantic entry point at each other: the file named in `Upstream`
        # must point back from its `Before use`, and vice versa.
        up = summary_of(ptext).get("Upstream", "")
        for sn in re.findall(r"2_semantic/([\w./-]+\.md)", up):
            if sn in semantic and name not in before_use(semantic[sn]):
                problems.append(f"one-way link: Upstream points to 2_semantic/{sn}, but its `Before use` does not point back to {name}")
        for sn in pointed_by:
            if f"2_semantic/{sn}" not in up and sn not in up:
                problems.append(f"one-way link: `Before use` in 2_semantic/{sn} points to {name}, but its Upstream does not point back")

    # INDEX.md is generated: regenerate it in memory and compare strings with the file on disk.
    # More reliable than mtimes: a git checkout shuffling timestamps causes no false alarm,
    # and a hand edit to INDEX.md cannot slip through.
    gen_index = MEM / "tools" / "gen_index.py"
    index_skipped = not gen_index.exists()
    if not index_skipped:
        r = subprocess.run([sys.executable, str(gen_index), "--check"], capture_output=True, text=True)
        if r.returncode != 0:
            problems.append(r.stdout.strip() or r.stderr.strip() or "gen_index.py --check failed")

    # Pointers in body text. A backticked path means "something that exists now".
    # Templates (< or *) and paths outside the repo cannot be checked.
    # 1_episodic/ and history/ are not scanned: they are records, and old paths in them are supposed to be old.
    scan = [ROOT / n for n in ("CLAUDE.md", "MEMORY_ARCH.md", "README.md")]
    scan += semantic_files
    scan += sorted((MEM / "3_procedural").glob("*.md"))
    for f in scan:
        if not f.exists():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            for m in re.findall(r"`([^`]+?\.md)`", line):
                if skip_ptr(m) or any((b / m).exists() for b in BASES):
                    continue
                problems.append(f"pointer not found: {m}   {f.relative_to(ROOT)}:{i}")
            # Directory pointers: backticked and ending in /.
            for m in re.findall(r"`([^`]+?/)`", line):
                if skip_ptr(m) or any((b / m).is_dir() for b in BASES):
                    continue
                problems.append(f"directory not found: {m}   {f.relative_to(ROOT)}:{i}")
            # Script paths in commands, even outside backticks. Only the `python3 <path>.py`
            # form is recognised; scanning whole code blocks would drown real warnings in noise.
            for m in re.findall(r"python3 ([^\s`\"']+\.py)", line):
                if skip_ptr(m) or any((b / m).exists() for b in BASES):
                    continue
                problems.append(f"script in command not found: {m}   {f.relative_to(ROOT)}:{i}")

    # Is the spec copy at the kit's version? The kit clone path is the "Kit clone" row in MEMORY_ARCH.md.
    # This compares against the local clone only; `git pull` in the kit fetches newer versions.
    ver = MEM / "spec" / "VERSION"
    if ver.exists():
        mine = ver.read_text(encoding="utf-8").split("\n")[0].strip()
        kit = None
        for arch in (ROOT / "MEMORY_ARCH.md", MEM / "MEMORY_ARCH.md"):
            if arch.exists():
                m = re.search(r"^\|\s*Kit clone\s*\|\s*`?([^`|]+?)`?\s*\|", arch.read_text(encoding="utf-8"), re.M)
                kit = Path(m.group(1)).expanduser() if m else None
                break
        if kit and (kit / "VERSION").exists():
            theirs = (kit / "VERSION").read_text(encoding="utf-8").strip()
            if theirs != mine:
                print(f"spec copy is v{mine}, the kit clone at {kit} is v{theirs}: "
                      f"follow sweep-check-spec-updates.md")
        else:
            print("kit clone not found (MEMORY_ARCH.md \"Kit clone\" row): cannot compare spec versions")
    else:
        print("no memory/spec/VERSION: the spec copy was not generated by the installer, or not generated yet")
    print(f"checked {checked} memory files")
    if not repo:
        print("skipped: not a git repo, so 'Visibility vs .gitignore' was not checked (not checked is not passed)")
    elif not remote:
        print("skipped: no remote, so the Private half of 'Visibility vs .gitignore' was not checked (Public-but-ignored still was)")
    if index_skipped:
        print("skipped: memory/tools/gen_index.py not found, INDEX.md was not checked")
    if times:
        gap = (datetime.datetime.now() - max(times)).total_seconds() / 3600
        flag = "WARNING: " if gap > 48 else ""
        print(f"{flag}hours since the latest episodic: {gap:.0f}")
    if tagcount:
        print(f"average tags per semantic file: {sum(tagcount)/len(tagcount):.1f} (a rising number is a signal)")
    if wt:
        print(f"{len(wt)} subagent worktrees left behind:")
        for w in wt:
            print(f"    {w.split('/')[-1]}")
        print("    => clean up when done: git worktree remove --force <path> && git branch -D worktree-<name>")
    # Two symptoms of the event layer leaking into the semantic layer. Shown by default,
    # not only under --format, because hidden signals go unnoticed.
    dated = []
    for _, name, bad in fmt:
        for b in bad:
            m = re.match(r"(\d+) lines with dates", b)
            if m:
                dated.append((int(m.group(1)), name))
    too_long = [name for _, name, bad in fmt for b in bad if "lines in total" in b]
    tot = len(semantic_files)
    if dated or too_long:
        print(f"event layer leaking into the semantic layer: {len(dated)}/{tot} files have dates in {memdoc.CONTENT}, "
              f"{sum(n for n, _ in dated)} lines in total; {len(too_long)} files over {memdoc.MAX_LINES} lines")
        for n, name in sorted(dated, reverse=True)[:5]:
            print(f"    {n:3d} dated lines  2_semantic/{name}")
        if len(dated) > 5:
            print(f"    ...and {len(dated) - 5} more. Use --format to see each line")
    if fmt:
        print(f"semantic files with format problems: {len(fmt)}/{tot} (--format for details):")
        for n, name, _ in sorted(fmt, reverse=True)[:5]:
            print(f"    {n:3d} problems  2_semantic/{name}")
        if len(fmt) > 5:
            print(f"    ...and {len(fmt) - 5} more")
    if "--format" in sys.argv:
        for n, name, bad in sorted(fmt, reverse=True):
            print(f"\n  2_semantic/{name} ({n})")
            for b in bad:
                print(f"    - {b}")
    if problems:
        print(f"\nFAIL: {len(problems)} problems:")
        for p in problems:
            print(f"  {p}")
        return 1
    print("OK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
