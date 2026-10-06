#!/usr/bin/env python3
"""Print this machine's timezone and the current time, and reconcile it with the
memory system's anchor timezone.

Runs on every user prompt, together with `sweep_due.py`.

* Why not just run `date`: `date` prints local time, but cannot show what it means for
  the memory system when this machine is no longer in the anchor timezone. The sweep
  line is fixed in the anchor timezone (see `sweep_due.py`), and episodic timestamps
  use it too. If the machine changes timezone, the two drift apart with no signal.

Usage:
  python3 memory/tools/UserPromptSubmit/now.py
    prints local timezone and time; if it differs from the anchor, also prints the
    anchor time and a warning.
  ⚠️ Always exits 0. It only prints, never judges, so chaining it with `&&` never blocks.
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# The memory system's anchor timezone (IANA name, e.g. "America/New_York").
# Timestamps and the sweep line use it. Keep it identical to ANCHOR_TZ in sweep_due.py.
# None = fall back to this machine's local timezone (no reconciliation is done).
ANCHOR_TZ = None
LOCALTIME = Path("/etc/localtime")


def zone_name():
    """The timezone name, and where it was read from.

    ⚠️ The TZ environment variable overrides the system setting for this process only,
    so the two sources are reported separately; otherwise "system set to A but this call
    overridden to B by TZ" would print as a false agreement.
    """
    if os.environ.get("TZ"):
        return f"{os.environ['TZ']} (TZ environment variable)"
    try:
        parts = LOCALTIME.resolve().parts
    except OSError:
        return "timezone name unreadable"
    if "zoneinfo" not in parts:
        return "timezone name unreadable"
    tz = "/".join(parts[len(parts) - parts[::-1].index("zoneinfo"):])
    return f"{tz} (system setting)"


def main():
    now = datetime.now().astimezone()
    print(f"Local  {now:%Y-%m-%d(%a) %H:%M:%S %Z%z}  [{zone_name()}]")

    if ANCHOR_TZ is None:
        return 0
    anchor = now.astimezone(ZoneInfo(ANCHOR_TZ))
    if now.utcoffset() != anchor.utcoffset():
        print(f"Anchor {anchor:%Y-%m-%d(%a) %H:%M:%S %Z}  [{ANCHOR_TZ}]")
        print(f"⚠️ This machine is not in {ANCHOR_TZ}. Use the Anchor line for timestamps")
        print("   and the sweep line; local time only tells you where the user is right now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
