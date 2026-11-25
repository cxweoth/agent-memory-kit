# promises-go-in-the-due-list

## Memory Summary
- Visibility: Public
- Brief: When you promise the user something that costs only your own time and has a due date: write it into memory/due.json on the spot
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-11-25

## Memory Content

- **When you promise something that costs only your own time and has a due date, write it into `memory/due.json` on the spot.** `python3 memory/tools/UserPromptSubmit/due.py --add "<due>" "<what>" "<source>"`, one row per item; `source` points to the episodic that records the promise, and if that is not written yet, add it on the sweep line. Items that have come due are printed into your context on every prompt: when done, run `due.py --done <number>` to delete the row; if you cannot do it, move the date and tell the user. Anything that costs the user's time, or needs the user's decision, does not go here: that belongs on the calendar.
