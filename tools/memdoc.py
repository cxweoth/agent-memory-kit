#!/usr/bin/env python3
"""Document model for memory files: parse into "Summary + a list of sections" and render back verbatim.

* Only the section level is structured. Each section's body is kept as an opaque
  string and never parsed further.
  => A byte-for-byte round trip is guaranteed by construction, not by luck. A general
     markdown AST cannot promise this, because it re-renders the whole document;
     this model never rebuilds a body.
  => The price is that inline markup (bold, links) is not parsed. That is deliberate:
     the memory system never edits inline markup, only whole sections and whole tables.

Why not an existing library: markdown-it-py yields a flat token stream rather than a
tree and only renders HTML, not markdown, so writing back would still be hand-rolled;
mistletoe has a markdown renderer but is not in the standard library, and "installed
on this machine" does not mean "installed on the next one".

Usage:
  python3 memory/tools/memdoc.py <file>                       print the Summary and the section index
  python3 memory/tools/memdoc.py <file> --section <fragment>  print the raw text of that section
  python3 memory/tools/memdoc.py <file> --find <keyword>      which sections mention it
  python3 memory/tools/memdoc.py --selftest                   built-in fixtures + round trip of every memory file

Writing is for programs; there is no CLI for it: `set_section` / `add_section` /
`retitle` / `remove_section` / `set_summary` / `save`, the `Table` object, and
`lint_semantic()` (validates one semantic file against the entry format).

Paths may be relative to the repo root or to `memory/`; both work.
"""
import re
import sys
from pathlib import Path

MEM = Path(__file__).resolve().parents[1]
ROOT = MEM.parents[0]

SUMMARY = "Memory Summary"
CONTENT = "Memory Content"

# Section split points. Summary fields are `- key: value`, one per line; ASCII and full-width colons both accepted.
_SPLIT = re.compile(r"(?m)^(#{2,6}) (.*)$")
_FIELD = re.compile(r"^-\s*(\S.*?)\s*[:：]\s*(.+?)\s*$", re.M)


class MemDoc:
    """One memory file. `sections` is a list of (level, title, body); body includes its trailing newlines."""

    def __init__(self, text: str, path: Path | None = None):
        self.text = text
        self.path = path
        m = re.match(r"# (.*)", text)
        self.title = m.group(1).strip() if m else None
        parts = _SPLIT.split(text)
        self.preamble = parts[0]          # between the H1 and the first ##; usually just the title
        self.sections = [(len(parts[i]), parts[i + 1], parts[i + 2])
                         for i in range(1, len(parts), 3)]

    # -- read ---------------------------------------------------------------
    @property
    def summary(self) -> dict:
        """Fields of the `## Memory Summary` section. This is the implicit contract shared by the tools."""
        for _, title, body in self.sections:
            if title.strip() == SUMMARY:
                return dict(_FIELD.findall(body))
        return {}

    def headings(self) -> list:
        """Section index: (level, title, content lines, table rows)."""
        out = []
        for lvl, title, body in self.sections:
            lines = [x for x in body.split("\n") if x.strip()]
            out.append((lvl, title.strip(), len(lines),
                        sum(1 for x in lines if x.lstrip().startswith("|"))))
        return out

    def section(self, fragment: str):
        """First section whose title contains `fragment`, as (title, raw body). None if not found."""
        for _, title, body in self.sections:
            if fragment in title:
                return title.strip(), body
        return None

    def find(self, needle: str) -> list:
        """Which sections mention `needle`, as (title, hit count).

        Only says where, never returns content; open the section to read it.
        This is deliberate: returning a snippet creates the "I already read it" mistake.
        """
        return [(t.strip(), b.count(needle))
                for _, t, b in self.sections if needle in b]

    # -- write --------------------------------------------------------------
    # Invariant: sections that were not named render back byte-for-byte. `--selftest` checks this.

    def render(self) -> str:
        """Rebuild the original text. Every memory file must round-trip exactly; that is this class's foundation."""
        return self.preamble + "".join(
            "#" * lvl + " " + title + body for lvl, title, body in self.sections)

    def _index(self, fragment: str) -> int:
        for i, (_, title, _) in enumerate(self.sections):
            if fragment in title:
                return i
        raise KeyError(f"no section whose title contains '{fragment}'")

    def set_section(self, fragment: str, body: str) -> None:
        """Replace a section's body. Leading/trailing newlines of `body` are normalised here.

        The number of newlines between the heading and the body is preserved. Hard-coding
        one newline would eat the blank line that markdown convention puts there.
        """
        i = self._index(fragment)
        lvl, title, old = self.sections[i]
        lead = len(old) - len(old.lstrip("\n")) or 1
        self.sections[i] = (lvl, title, "\n" * lead + body.strip("\n") + "\n\n")

    def add_section(self, level: int, title: str, body: str,
                    after: str | None = None) -> None:
        """Insert a section. `after` is a fragment of an existing title; omitted means append at the end."""
        item = (level, title, "\n" + body.strip("\n") + "\n\n")
        self.sections.insert(self._index(after) + 1 if after else len(self.sections), item)

    def retitle(self, fragment: str, title: str) -> None:
        """Change a section's title; the body is untouched."""
        i = self._index(fragment)
        lvl, _, body = self.sections[i]
        self.sections[i] = (lvl, title, body)

    def remove_section(self, fragment: str) -> list:
        """Remove a section together with its deeper subsections; return the removed (level, title, body) list.

        The return value is for the caller to report item by item: deleting requires the
        user's confirmation (`memory/3_procedural/no-delete-by-default.md`), so the caller
        must be able to say exactly what was removed.
        """
        i = self._index(fragment)
        lvl = self.sections[i][0]
        j = i + 1
        while j < len(self.sections) and self.sections[j][0] > lvl:
            j += 1
        gone = self.sections[i:j]
        del self.sections[i:j]
        return gone

    def set_summary(self, field: str, value: str) -> None:
        """Set one Summary field. If the field is missing, append it after the last field."""
        i = self._index(SUMMARY)
        lvl, title, body = self.sections[i]
        line = f"- {field}: {value}"
        new, n = re.subn(rf"(?m)^-\s*{re.escape(field)}\s*[:：].*$", lambda _: line, body, count=1)
        if not n:
            fields = list(_FIELD.finditer(body))
            if not fields:
                raise KeyError("the Summary has no fields at all; refusing to guess where to insert")
            end = fields[-1].end()
            new = body[:end] + "\n" + line + body[end:]
        self.sections[i] = (lvl, title, new)

    def table(self, fragment: str):
        """First table in that section as a `Table` (None if there is none). Write back with `set_table`."""
        hit = self.section(fragment)
        return Table.parse(hit[1]) if hit else None

    def set_table(self, fragment: str, tbl: "Table") -> None:
        """Replace the first table in that section with `tbl`; lines outside the table are kept as they are."""
        i = self._index(fragment)
        lvl, title, body = self.sections[i]
        lines = body.split("\n")
        start = next((j for j, l in enumerate(lines)
                      if l.strip().startswith("|")
                      and j + 1 < len(lines) and set(lines[j + 1].strip()) <= set("|-: ")), None)
        if start is None:
            raise KeyError(f"section '{fragment}' has no table")
        end = start + 2
        while end < len(lines) and lines[end].strip().startswith("|"):
            end += 1
        self.sections[i] = (lvl, title,
                            "\n".join(lines[:start] + tbl.render().split("\n") + lines[end:]))

    def save(self, path: Path | None = None) -> Path:
        """Write back to disk.

        Refuses to write into `1_episodic/consolidated/`. Those files are the record of
        what happened, and episodic memory by definition is never rewritten. Semantic and
        procedural files are the opposite: being rewritten is what they are for.
        """
        dest = path or self.path
        if dest is None:
            raise ValueError("no path to write to")
        dest = Path(dest).resolve()
        # Only files under this copy of the repo may be written. A memdoc running inside a
        # worktree has that worktree as ROOT, so it cannot write into the main checkout,
        # even with an absolute path. Likewise the main checkout's memdoc must not write
        # into a worktree: that is another agent's scratch area.
        if ".claude/worktrees" in dest.as_posix() and ".claude/worktrees" not in ROOT.as_posix():
            raise PermissionError(f"refusing to write into another agent's worktree: {dest}")
        if not dest.is_relative_to(ROOT):
            raise PermissionError(
                f"refusing to write outside this repo: {dest}\n"
                f"   this memdoc's scope is {ROOT}\n"
                f"   inside a worktree it may only write that worktree.")
        if "1_episodic/consolidated" in dest.as_posix():
            raise PermissionError(
                f"refusing to write a consolidated episodic: {dest.name}\n"
                f"   it is a record. To change what it says, extract the facts into 2_semantic/ and leave the original alone.")
        dest.write_text(self.render(), encoding="utf-8")
        return dest


# -- standard blocks ------------------------------------------------------

class Table:
    """A table: headers + rows. It is data, not a string, so it can be read back and edited.

    Rendering has exactly one shape, so "align the columns or not" is not a choice:
    the same data always renders to the same string.
    """

    def __init__(self, headers: list, rows: list | None = None):
        self.headers = [str(h).strip() for h in headers]
        self.rows = [[str(c).strip() for c in r] for r in (rows or [])]

    @classmethod
    def parse(cls, text: str):
        """Read the first table in a block of text. None if there is none."""
        lines = [l.strip() for l in text.split("\n")]
        for i, l in enumerate(lines):
            if l.startswith("|") and i + 1 < len(lines) and set(lines[i + 1]) <= set("|-: "):
                cells = lambda s: [c.strip() for c in s.strip("|").split("|")]
                headers = cells(l)
                rows = []
                for r in lines[i + 2:]:
                    if not r.startswith("|"):
                        break
                    rows.append(cells(r))
                return cls(headers, rows)
        return None

    def add_row(self, row: list) -> "Table":
        if len(row) != len(self.headers):
            raise ValueError(f"this table has {len(self.headers)} columns, got {len(row)}")
        self.rows.append([str(c).strip() for c in row])
        return self

    def render(self) -> str:
        out = ["| " + " | ".join(self.headers) + " |",
               "|" + "|".join("---" for _ in self.headers) + "|"]
        out += ["| " + " | ".join(r) + " |" for r in self.rows]
        return "\n".join(out)

    def __len__(self):
        return len(self.rows)

    def __repr__(self):
        return f"Table({len(self.headers)} cols x {len(self.rows)} rows: {', '.join(self.headers)})"


def table(headers: list, rows: list | None = None) -> str:
    """Render a table to a string. Use a `Table` object if it needs to be edited later."""
    return Table(headers, rows).render()


# -- semantic file format -------------------------------------------------
# Level 2 is fixed: exactly these two sections, in this order, and no other level-2 sections.
SEMANTIC_TOP = (SUMMARY, CONTENT)
# Level 3 under `## Memory Content` is an entry; its title is the term being looked up.
# The first line of an entry is the main definition or claim; the fields below follow in
# this order, one `* Field: ...` per line. They are body text, not subsections.
ENTRY_FIELDS = ("Prerequisites", "Derived", "Disambiguation", "Source", "Inputs",
                "Premises", "Changes when", "Confirmed", "Before use")
# Dates may only live in these fields (and in paths into 1_episodic/, whose file names carry a date).
DATE_FIELDS = ("Confirmed", "Source")
# Entry titles that are category names rather than the term being looked up.
CATEGORY_TITLES = ("definition", "definitions", "fact", "facts", "derivation", "derivations",
                   "judgment", "judgement", "check", "checks", "criterion", "criteria")

MAX_LINES = 200

# Only YYYY-MM-DD is recognised, since it is the only date format the system writes.
_DATE = re.compile(r"20\d\d-\d\d-\d\d")
_EMPTY_FIELD = re.compile(r"^\s*[-*]\s*\S[^:：]*[:：]\s*(none|None|N/A|n/a|—|-|none\.|None\.|TBD)\s*$")
# A list marker must be followed by whitespace; `**bold**:` is not a field.
_FIELD_LINE = re.compile(r"^\s*[-*]\s+([^:：\s][^:：]*?)\s*[:：]")


def _lint_common(doc: MemDoc) -> tuple:
    """File-level checks. Returns (problems, after); `after` is the sections following `## Memory Content`."""
    bad = []
    if not doc.title:
        bad.append("no H1 title")
    hit = doc.section(CONTENT)
    if hit is None:
        return bad + [f"no `## {CONTENT}`"], None
    lv2 = [t.strip() for l, t, _ in doc.sections if l == 2]
    if lv2 != list(SEMANTIC_TOP):
        bad.append(f"level-2 sections must be exactly {', '.join(SEMANTIC_TOP)}, in that order; found {lv2}")
    for lvl, title, _ in doc.sections[:doc._index(CONTENT)]:
        if lvl > 2:
            bad.append(f"no subsections allowed before `## {CONTENT}`; found level {lvl} '{title.strip()}'")
    after = doc.sections[doc._index(CONTENT) + 1:]

    # Content lives in subsections; `hit[1]` is only the lines directly under `## Memory Content`.
    n = len([x for x in hit[1].split("\n") if x.strip()])
    n += sum(1 + len([x for x in body.split("\n") if x.strip()]) for _, _, body in after)
    # The above counts non-blank content lines; the limit applies to the raw line count,
    # which is the length a reader actually sees.
    raw = len(doc.text.split("\n"))
    if raw > MAX_LINES:
        bad.append(f"{raw} lines in total ({n} content lines), over {MAX_LINES}: split or consolidate")

    # The semantic layer holds what is true now; dates belong to the event layer.
    # Allowed: the Summary (`Upstream`, `Updated`), the date fields, and paths into 1_episodic/.
    def date_allowed(l: str) -> bool:
        if "1_episodic/" in l:
            return True
        f = _FIELD_LINE.match(l)
        return bool(f and f.group(1).strip() in DATE_FIELDS)
    dated = [l.strip() for l in ("".join(b for _, _, b in
                                 doc.sections[doc._index(CONTENT):])).split("\n")
             if _DATE.search(l) and not date_allowed(l)]
    if dated:
        head = "; ".join(x[:38] for x in dated[:3])
        bad.append(f"{len(dated)} lines with dates in {CONTENT} => that belongs to the event layer. First three: {head}")
    return bad, after


def _lint_entries(after: list) -> list:
    bad = []
    lv3 = [t.strip() for l, t, _ in after if l == 3]
    if not lv3:
        bad.append(f"no entries under `## {CONTENT}` (a level-3 title is the term being looked up)")
    seen = set()
    for lvl, title, body in after:
        t = title.strip()
        if lvl == 3:
            if t in seen:
                bad.append(f"entry '{t}' appears twice; one fact has one home")
            seen.add(t)
            if t.lower() in CATEGORY_TITLES:
                bad.append(f"entry title '{t}' is a category name, not the term being looked up")
            lines = [x for x in body.split("\n") if x.strip()]
            if not lines:
                bad.append(f"entry '{t}' is empty; its first line should be the answer")
            elif re.match(r"([*-]\s|[>|])", lines[0].lstrip()):   # a real list / quote / table; `**term**` bold is fine
                bad.append(f"entry '{t}': first line is not the main definition (it is a list/quote/table); the answer goes on the first line")
        elif lvl > 3:
            bad.append(f"entries go only to level 3; found level {lvl} '{t}' (Prerequisites, Derived, Disambiguation, Before use are body fields, not subsections)")
        seen_fields = []
        for l in body.split("\n"):
            if _EMPTY_FIELD.match(l):
                bad.append(f"'{t}' has an empty placeholder field: {l.strip()[:30]} (if there is no content, omit the field)")
            f = _FIELD_LINE.match(l)
            if f and lvl == 3:
                name = f.group(1).strip()
                if name not in ENTRY_FIELDS:
                    bad.append(f"entry '{t}': field '{name}' is not in the spec's field table ({' / '.join(ENTRY_FIELDS)})")
                else:
                    seen_fields.append(name)
        order = [x for x in ENTRY_FIELDS if x in seen_fields]
        if seen_fields != order and len(set(seen_fields)) == len(seen_fields):
            bad.append(f"entry '{t}': fields must follow the order {' -> '.join(ENTRY_FIELDS)}; found {seen_fields}")
    return bad


def lint_semantic(doc: MemDoc) -> list:
    """Does a semantic file follow the format? Returns a list of problems; empty means it does.

    Not checked: "is this written as a narrative?" The real test is "does this sentence
    say what is true now, or what happened back then?", and dates are only a proxy for it.
    That one can only be upheld while writing.
    """
    bad, after = _lint_common(doc)
    if after is None:
        return bad
    return bad + _lint_entries(after)


def load(arg: str) -> MemDoc:
    for base in (Path.cwd(), ROOT, MEM):
        p = base / arg
        if p.is_file():
            return MemDoc(p.read_text(encoding="utf-8"), p)
    raise SystemExit(f"not found: {arg}")


# -- self-test --------------------------------------------------------------

_GOOD = """# Reward shaping

## Memory Summary

- Visibility: Public
- Tags: rl
- Brief: What reward shaping means in this project.
- Admission: Definitions and claims about reward shaping; no run logs.
- Open when: Designing or reviewing a reward function.
- Upstream: `1_episodic/consolidated/2025-01-02_reward.md`
- Updated： 2025-01-03

## Memory Content

### Potential-based shaping

Adding F(s, s') = γΦ(s') − Φ(s) to the reward; it leaves the optimal policy unchanged.
* Prerequisites: 1. Φ is a function of state only.
* Source: `1_episodic/consolidated/2025-01-02_reward.md`
* Changes when: the discount factor is changed mid-training.
* Confirmed: 2025-01-02
* Before use: `3_procedural/check-shaping-terms.md`
"""

_BAD = """# Bad file

## Memory Summary

- Visibility: Public

## Memory Content

### Facts

* Source: none
On 2025-01-05 we decided this.

#### Too deep

text
"""


def _fixtures() -> list:
    """Built-in fixtures. Returns a list of failure messages; empty means all passed."""
    fail = []
    good = MemDoc(_GOOD)
    if good.render() != _GOOD:
        fail.append("good fixture does not round-trip")
    s = good.summary
    if s.get("Visibility") != "Public" or s.get("Updated") != "2025-01-03":
        fail.append(f"summary parse (ASCII and full-width colon) wrong: {s}")
    if lint_semantic(good):
        fail.append(f"good fixture should lint clean, got: {lint_semantic(good)}")
    if good.headings()[-1][1] != "Potential-based shaping":
        fail.append("section index wrong")

    bad = lint_semantic(MemDoc(_BAD))
    for expect in ("category name", "empty placeholder", "lines with dates", "only to level 3"):
        if not any(expect in b for b in bad):
            fail.append(f"bad fixture: expected a problem mentioning '{expect}', got {bad}")

    doc = MemDoc(_GOOD)
    doc.set_summary("Updated", "2025-02-01")
    doc.set_summary("Scope", "universal")
    if doc.summary.get("Updated") != "2025-02-01" or doc.summary.get("Scope") != "universal":
        fail.append(f"set_summary failed: {doc.summary}")
    before = doc.render()
    doc.set_section("Potential-based shaping", "New main definition.")
    after = doc.render()
    if before.split("### Potential-based shaping")[0] != after.split("### Potential-based shaping")[0]:
        fail.append("set_section changed sections it was not asked to change")
    gone = doc.remove_section("Potential-based shaping")
    if len(gone) != 1 or doc.section("Potential-based shaping"):
        fail.append("remove_section failed")

    t = Table(["Term", "Meaning"]).add_row(["Φ", "potential"])
    if Table.parse(t.render()).rows != [["Φ", "potential"]]:
        fail.append("Table round trip failed")
    return fail


def selftest() -> int:
    """Built-in fixtures, then a round trip of every memory file. No test framework; this is the self-check."""
    fail = _fixtures()
    print(f"fixtures: {'all passed' if not fail else f'{len(fail)} failed'}")
    for f in fail:
        print(f"  x {f}")
    bad = []
    files = sorted(p for p in MEM.rglob("*.md") if p.name != "INDEX.md")
    for p in files:
        t = p.read_text(encoding="utf-8")
        if MemDoc(t, p).render() != t:
            bad.append(p.relative_to(ROOT))
    print(f"round trip of {len(files)} memory files: {len(files) - len(bad)} exact, {len(bad)} mismatched")
    for p in bad:
        print(f"  x {p}")
    noh1 = [p.relative_to(ROOT) for p in files
            if MemDoc(p.read_text(encoding="utf-8"), p).title is None]
    if noh1:
        print(f"warning: {len(noh1)} without an H1 title: {[str(x) for x in noh1]}")
    return 1 if bad or fail else 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2 if not args else 0
    if args[0] == "--selftest":
        return selftest()

    doc = load(args[0])
    rest = args[1:]

    if rest and rest[0] == "--section":
        hit = doc.section(" ".join(rest[1:]))
        if not hit:
            print(f"no section whose title contains '{' '.join(rest[1:])}'")
            print("   available: " + ", ".join(h[1] for h in doc.headings()))
            return 1
        title, body = hit
        print(f"## {title}{body}", end="")
        others = [h[1] for h in doc.headings() if h[1] != title]
        print(f"\nnote: {len(others)} other sections in this file were not printed: " + ", ".join(others))
        return 0

    if rest and rest[0] == "--find":
        needle = " ".join(rest[1:])
        hits = doc.find(needle)
        print(f"'{needle}' appears in {len(hits)} sections (location only; open the section to read it):")
        for title, n in hits:
            print(f"  {n:2d}x  {title}")
        return 0 if hits else 1

    s = doc.summary
    print(f"# {doc.title}")
    if doc.path:
        p = doc.path.resolve()
        print(f"  {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}")
    for k in ("Visibility", "Tags", "Brief", "Admission", "Open when", "Upstream", "Updated"):
        if k in s:
            print(f"  {k}: {s[k]}")
    hs = doc.headings()
    total = sum(h[2] for h in hs)
    print(f"\nSection index ({len(hs)} sections, {total} content lines)")
    print(f"{'lines':>5}{'rows':>5}  title")
    for lvl, title, n, t in hs:
        print(f"{n:5d}{t:5d}  {'  ' * (lvl - 2)}{title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
