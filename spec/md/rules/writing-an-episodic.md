# writing-an-episodic

## Memory Summary
- Visibility: Public
- Brief: When writing an episodic: what one episodic holds, and which fields are mandatory
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-09-20

## Memory Content

- **Episodics are never rewritten.** An episodic records what was true at the time, and is allowed to go out of date.
- **Every episodic has `Errors caught by`.** Source names must match `SOURCES` in `memory/tools/tally.py` exactly; an item that does not match is not counted. `unrecorded` is not zero: it was never measured, so it is left out of the denominator.
