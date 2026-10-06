#!/usr/bin/env python3
"""Set up an agent's memory system from this kit.

  python3 install.py [AGENT_DIR] --agent NAME --user NAME [--hook]

AGENT_DIR is the agent's project root (default: current directory). It gets:

  memory/1_episodic/consolidated/   memory/2_semantic/history/   memory/3_procedural/history/
  memory/tools/        the kit's tools
  memory/spec/         the spec copy, generated from spec/spec.json
  memory/3_procedural/ the universal rule files, Upstream pointing at the import episodic
  memory/1_episodic/   one episodic recording this import
  data/                material that is not memory
  MEMORY_ARCH.md       this agent's own settings (owner, tags, error sources)
  CLAUDE.md            a Memory section with the dispatch table (appended if CLAUDE.md exists)
  .claude/settings.json  the UserPromptSubmit hook, only with --hook (merged, never replaced)

Safe to re-run: existing files are never overwritten; what was skipped is reported.
To update an installed agent later, follow the sweep rule `sweep-check-spec-updates.md`.
Python 3 stdlib only.
"""
import argparse, datetime, json, shutil, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
PLACEHOLDER = "<the episodic that recorded importing this spec>"


def say(kind, msg):
    print(f"  {kind:<8} {msg}")


def copy_tools(dst):
    for src in sorted((KIT / "tools").rglob("*.py")):
        rel = src.relative_to(KIT / "tools")
        out = dst / rel
        if out.exists():
            if out.read_bytes() != src.read_bytes():
                say("skip", f"memory/tools/{rel} exists and differs from the kit (update with gen_spec.py --get)")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        say("add", f"memory/tools/{rel}")


def write_new(path, text, label):
    if path.exists():
        say("skip", f"{label} already exists")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    say("add", label)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("agent_dir", nargs="?", default=".")
    ap.add_argument("--agent", required=True, help="the agent's name (it owns the memory)")
    ap.add_argument("--user", required=True, help="the name of the user the agent works for")
    ap.add_argument("--hook", action="store_true", help="also add the UserPromptSubmit hook to .claude/settings.json")
    a = ap.parse_args()

    root = Path(a.agent_dir).resolve()
    mem = root / "memory"
    version = (KIT / "VERSION").read_text(encoding="utf-8").strip()
    now = datetime.datetime.now().astimezone()
    today = now.date().isoformat()
    print(f"agent-memory-kit v{version} -> {root}")

    for d in ("1_episodic/consolidated", "2_semantic/history", "3_procedural/history", "tools"):
        (mem / d).mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(exist_ok=True)

    copy_tools(mem / "tools")

    r = subprocess.run([sys.executable, str(mem / "tools" / "gen_spec.py"), str(KIT / "spec" / "spec.json"), str(mem / "spec")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"gen_spec.py failed:\n{r.stdout}{r.stderr}")
    say("gen", f"memory/spec/ (v{version})")

    ep_name = f"{today}_import-agent-memory-kit.md"
    ep_rel = f"1_episodic/{ep_name}"
    if not list((mem / "1_episodic").rglob("*_import-agent-memory-kit.md")):
        rules = sorted(p.name for p in (mem / "spec" / "rules").glob("*.md"))
        write_new(mem / ep_rel, f"""# Imported agent-memory-kit v{version}

## Memory Summary
- Visibility: Public
- Brief: {a.agent} set up its memory system from agent-memory-kit v{version} for {a.user}
- Occurred: {now:%Y-%m-%d %H:%M}–{now:%H:%M} {now:%Z}
- Transcript: none (written by install.py)
- Procedurals used: none
- Errors caught by: none

## Memory Content

- Ran `install.py` from the kit at `{KIT}`.
- Generated the spec copy in `memory/spec/` and copied the kit's tools into `memory/tools/`.
- Imported {len(rules)} universal rule files into `memory/3_procedural/`: {", ".join(rules)}.
""", f"memory/{ep_rel}")
    else:
        ep_rel = "1_episodic/" + next((mem / "1_episodic").rglob("*_import-agent-memory-kit.md")).relative_to(mem / "1_episodic").as_posix()

    for src in sorted((mem / "spec" / "rules").glob("*.md")):
        text = src.read_text(encoding="utf-8").replace(PLACEHOLDER, f"`{ep_rel}`")
        write_new(mem / "3_procedural" / src.name, text, f"memory/3_procedural/{src.name}")

    arch = (KIT / "templates" / "MEMORY_ARCH.md").read_text(encoding="utf-8")
    write_new(root / "MEMORY_ARCH.md", arch.format(agent=a.agent, user=a.user, kit=KIT), "MEMORY_ARCH.md")

    claude = root / "CLAUDE.md"
    block = (KIT / "templates" / "CLAUDE.md").read_text(encoding="utf-8")
    if not claude.exists():
        write_new(claude, f"# {a.agent}\n\n{block}", "CLAUDE.md")
    elif "DISPATCH:START" not in claude.read_text(encoding="utf-8"):
        with claude.open("a", encoding="utf-8") as f:
            f.write("\n\n" + block)
        say("append", "CLAUDE.md (Memory section)")
    else:
        say("skip", "CLAUDE.md already has a dispatch table")

    if a.hook:
        sp = root / ".claude" / "settings.json"
        cfg = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
        hook = json.loads((KIT / "templates" / "settings.json").read_text(encoding="utf-8"))["hooks"]["UserPromptSubmit"][0]
        lst = cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
        if any("emit.py" in h.get("command", "") for e in lst for h in e.get("hooks", [])):
            say("skip", ".claude/settings.json already has the emit.py hook")
        else:
            lst.append(hook)
            sp.parent.mkdir(exist_ok=True)
            sp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            say("hook", ".claude/settings.json (UserPromptSubmit -> emit.py)")

    for tool in ("gen_dispatch.py", "gen_index.py"):
        r = subprocess.run([sys.executable, str(mem / "tools" / tool)], capture_output=True, text=True, cwd=root)
        say("run", f"{tool} (exit {r.returncode})")

    print(f"""
Done. Next:
  1. Edit MEMORY_ARCH.md: add the tags this agent needs.
  2. {"Hook installed." if a.hook else "Add the hook in templates/settings.json to .claude/settings.json (or re-run with --hook)."}
  3. Check everything: python3 memory/tools/memory_check.py
  4. Commit memory/ to the agent's own git repo. Private files stay off remotes.""")


if __name__ == "__main__":
    main()
