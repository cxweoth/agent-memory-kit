# no-delete-by-default

## Memory Summary
- Visibility: Public
- Brief: Make append-only and safe changes directly; deleting, renaming, moving, or marking obsolete starts with a list and waits for the user to confirm
- Upstream: <the episodic that recorded importing this spec>
- Access: Triggered
- Scope: universal
- Updated: 2026-09-20

## Memory Content

- **No deletion by default.** Append-only and reversible changes are made directly, then you report which files and which lines were touched; deleting, renaming, moving, or marking as obsolete always starts with a list and waits for the user to confirm (which file, how many lines, why it is obsolete, where the content still lives). The only thing that may be deleted directly is a superseded old statement in `2_semantic/`, and each deleted sentence is listed in the commit message.
- **Before anything is deleted, the original text must have a home as evidence**, pointed to in the list; "it has already been extracted" is not a reason. Retired Semantic and Procedural files move in whole into that layer's `2_semantic/history/` or `3_procedural/history/`; content cut from a rule file is written into the day's `1_episodic/`.
- **Do not decide whether to keep a file you cannot open** (PDFs, images, binaries). Say "I have not read it" first, and let the user decide.
