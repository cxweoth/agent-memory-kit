#!/usr/bin/env python3
"""Decide whether there are episodics not yet swept. Runs on every user prompt,
together with `now.py`.

The rule is `sweep-write-todays-episodics.md`.
The state file `1_episodic/_sweep_state.json` records a single moment: how far the
last sweep covered.

* Why a state file rather than the date of the newest episodic: it distinguishes
  "swept, nothing to record that day" from "never swept". The former produces no
  file, so deriving from file names would rescan the same span every day.

Usage:
  python3 memory/tools/UserPromptSubmit/sweep_due.py         check. exit 1 = sweep due
  python3 memory/tools/UserPromptSubmit/sweep_due.py --done  stamp
  ⚠️ Run --done only after the episodics are written. In the wrong order the state
     says "swept" while the entry was never written, and that error has no signal.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# The memory system's anchor timezone (IANA name, e.g. "America/New_York").
# Keep it identical to ANCHOR_TZ in now.py.
# None = fall back to this machine's local timezone.
ANCHOR_TZ = None
# The daily sweep line, in the anchor timezone. Set it to when the user's day winds down.
SWEEP_HOUR, SWEEP_MINUTE = 18, 0

TZ = ZoneInfo(ANCHOR_TZ) if ANCHOR_TZ else datetime.now().astimezone().tzinfo
STATE = Path(__file__).resolve().parents[2] / "1_episodic" / "_sweep_state.json"


def last_cutoff(now):
    """The most recent sweep line already passed. This one comparison covers both
    "past today's sweep line and not swept yet" and "nothing swept all of yesterday,
    woken up this morning"."""
    t = now.replace(hour=SWEEP_HOUR, minute=SWEEP_MINUTE, second=0, microsecond=0)
    return t if now >= t else t - timedelta(days=1)


def main():
    now = datetime.now(TZ)
    due_by = last_cutoff(now)

    if "--done" in sys.argv:
        # Record due_by, not now: the range the state file claims must equal the range it
        # actually covers. Whoever stamps has covered up to the sweep line they were called
        # for, not up to the moment they pressed the button. Behaviourally the two are
        # equivalent (no sweep line lies in (due_by, now]); the difference is the truth of
        # the record, and whether the multi-day cold-start warning fires when it should.
        STATE.write_text(json.dumps({"last_swept": due_by.isoformat()},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
        nxt = last_cutoff(now + timedelta(days=1))
        print(f"✅ Stamped: covered up to {due_by:%Y-%m-%d %H:%M}")
        print(f"   ⚠️ Next sweep line {nxt:%Y-%m-%d %H:%M} not covered yet")
        return 0

    if not STATE.exists():
        print("⚠️ Sweep due: no state file, treated as never swept")
        print(f"   Cover up to: {due_by:%Y-%m-%d %H:%M}")
        return 1

    last = datetime.fromisoformat(
        json.loads(STATE.read_text(encoding="utf-8"))["last_swept"])
    if last >= due_by:
        nxt = last_cutoff(now + timedelta(days=1))
        print(f"✅ No sweep needed (last swept up to {last:%Y-%m-%d %H:%M}, "
              f"next sweep line {nxt:%Y-%m-%d %H:%M})")
        return 0

    gap = (due_by.date() - last.date()).days
    print("⚠️ Episodic sweep due")
    print(f"   Last swept up to: {last:%Y-%m-%d %H:%M}")
    print(f"   Cover up to:      {due_by:%Y-%m-%d %H:%M} ({gap} day(s) span)")
    if gap >= 1:
        print("   ⚠️ More than a day has passed; those days are a cold start. The only evidence")
        print("      is git log, calendar, and file mtimes; transcripts may only cover the most")
        print("      recent sessions. Mark backfilled content as reconstructed, not remembered.")
    print("   => Write 1_episodic/ first, then run --done")
    return 1


if __name__ == "__main__":
    sys.exit(main())
