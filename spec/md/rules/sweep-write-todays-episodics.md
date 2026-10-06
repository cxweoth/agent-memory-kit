# sweep-write-todays-episodics

## Memory Summary
- Visibility: Public
- Brief: When the sweep line says it is due, first write the day's episodics, and only then answer the user
- Upstream: <the episodic that recorded importing this spec>
- Access: Boot
- Scope: universal
- Updated: 2026-09-20

## Memory Content

- **When the sweep line is due, first write the day's episodics, and only then answer the user.** If you do not see the sweep line, run `python3 memory/tools/UserPromptSubmit/sweep_due.py` yourself; exit code 1 means it is due. Order: scan what happened in that span, one episodic per event, recording user decisions per `3_procedural/decision-attribution.md` → `python3 memory/tools/gen_index.py` → check for spec updates per `3_procedural/sweep-check-spec-updates.md` → finally stamp with `sweep_due.py --done`. The order may not be changed, and an empty day gets stamped too.
- **A sweep line that spans more than one day is a cold start**: write only what the evidence supports, and mark it as reconstructed from evidence. You are filling in a record, not making a judgment.
