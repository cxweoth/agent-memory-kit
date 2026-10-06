# Semantic memory

<!-- Generated file; do not edit by hand. Source: Memory System Specification v59; generated on 2026-10-07 -->

`2_semantic/`

## File names

- **The file name is the home of the fact**; the file system guarantees it is unique.
- **A file specific to one project gets the project name as a prefix**, `<proj>_<fact>.md`; a cross-project file does not, because a prefix would imply it belongs to one project. The prefix is a flat naming convention, not a hierarchy.

## The skeleton of Memory Content

```
# Title
└ ## Memory Content
   └ ### Entry name = the term being looked up
       ├ Main definition, or claim
       ├ Fields after the main definition, one * Field:  per line; see the table below
       └ Before use
```

- Level 3 is the **entry**, and **its heading is the term being looked up** (e.g. `### Empowerment`); a fact entry uses the phrase you would search for. **Do not write a category name** (definition, fact, derivation), **and do not write a sentence**: the answer is on the entry's first line, while the heading is the target of pointers and must stay stable.
- **The first line of an entry is the answer** (the main definition or the claim); after it, fields go one per line as `* Field: `, in the order of the table below. **Only the main definition is required**; any other field with no content is omitted entirely, never left empty.
- **Before use** holds one pointer per line to the checks in `3_procedural/` derived from this entry. **You see them as soon as you read the entry**, without having to remember to search.

## Fields allowed under an entry

| Field | What to write |
|---|---|
| `Prerequisites` | Terms the main definition uses, numbered; a later one may use the earlier ones |
| `Derived` | Terms derived from the main definition |
| `Disambiguation` | Outside uses of the same name with a different meaning (e.g. what the literature calls X is called Y in this file) |
| `Source` | The path to the upstream episodic, or `unverified`. **An episodic file name carries a date; that date is not a violation** |
| `Inputs` | Only for derived entries: which facts it is derived from; if an input changes, the entry silently goes stale |
| `Premises` | Only for judgments: if a premise changes, re-evaluate the entry |
| `Changes when` | The invalidation condition; written only when it is not obvious |
| `Confirmed` | The date this fact was last confirmed or computed. **Dates may appear only in this field and in `Source` paths**; a date in a sentence is narrative, which belongs to the episodic layer |
| `Before use` | One pointer per line to the checks in `3_procedural/` derived from this entry |

- Anything that is not a field name in this table is not written as `* X: `. `memdoc.py` reports fields that are not in this table.
