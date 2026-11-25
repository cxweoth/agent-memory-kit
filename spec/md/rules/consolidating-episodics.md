# consolidating-episodics

## Memory Summary
- Visibility: Public
- Brief: An episodic is consolidated when it has been fully extracted, not when the work is done; first extract what belongs in the upper layers, then move it; one fixed sweep line every week clears them all
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-11-25

## Memory Content

- **Whether an episodic is consolidated depends on whether it has been fully extracted, not on whether the work is done.** First extract whatever the upper layers have not yet captured (thresholds per the entry rules 1–5), then move it: `python3 memory/tools/mem_mv.py 1_episodic/<file>.md 1_episodic/consolidated/<file>.md --apply`.
- **On one fixed sweep line every week, extract the episodics into the semantic layer, and stamp only when none are left.** Which day is written in `MEMORY_ARCH.md` under "Weekly extraction day". On that day, after writing the day's episodics, extract every episodic still in `1_episodic/` one by one per `3_procedural/before-extracting-semantic.md` and move each into `1_episodic/consolidated/` per the previous rule; put everything that needs the user's ruling into one table and ask once, leaving those episodics where they are. Run `sweep_due.py --done` only when `1_episodic/` holds nothing but the ones awaiting a ruling.
