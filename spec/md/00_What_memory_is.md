# What memory is

<!-- Generated file; do not edit by hand. Source: Memory System Specification v60; generated on 2026-10-07 -->

`Definitions and principles`

## Memory and its owner

- **Memory**: the process involved in the acquisition, storage, and retrieval of information.
- **The memory owner is the agent, not the user.** The agent stores the user's information in its own memory area, and uses that memory to help the user.

## The three kinds of memory

| Kind | Definition | One-line test | How to look it up |
|---|---|---|---|
| **Episodic** | memory of personally experienced events, bound to a specific time and place. | Things that happened. **Never rewritten** | Browse by time |
| **Semantic** | general knowledge of facts and concepts, independent of when and where it was acquired. | Facts as they are now. **Gets rewritten** | Find the file by tag, then the entry by heading |
| **Procedural** | memory of how to perform an action, acquired gradually through repetition, expressed by doing rather than by recalling. | How to do things. Compiled from repeated failure episodics, or derived from semantic facts | Loaded at boot, or triggered |

## How memory flows

- What happens in a conversation first becomes **Episodic**; facts without a time, extracted from Episodic, become **Semantic**; repeated failures, or practices derived from facts, become **Procedural**. The user can also set a Procedural directly, on the spot.
- Episodic is the ultimate source of all memory. Memory always moves forward in time, so this design cannot produce a cycle.
- The threshold for each path is in the five entry rules at the top of the rule table (rules 1–5).
