# Semantic memory

<!-- Generated file; do not edit by hand. Source: Memory System Specification v62; generated on 2026-11-25 -->

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
       ├ Fields after the main definition, one * Field: per line; see the table below
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

## How to find things

- **The structure has two halves: building the table is slow and weekly; searching is fast and happens every turn.** Relying only on the list of semantic files that `mem_recall.py` prints, and guessing from a one-line brief which file to open, guesses wrong once there are many files, and misses the same meaning written in different words.
- **Building the table** (`mem_keywords.py`): only `2_semantic/` and `3_procedural/` are indexed, never episodics or `history/`. Split into sentences → segment into words → tag parts of speech and keep only nouns and verbs → one candidate list per file → use a sentence-embedding model (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) to score how close each word is to its file, and keep 8 per file → use the same model to merge words of similar meaning into one group → write `memory/index/keywords.json`: each group of words maps to the files it came from. The source spec is written for Chinese text and uses `ckiplab/bert-base-chinese-ws` to segment and `ckiplab/bert-base-chinese-pos` to tag; use a segmenter and tagger for your own language.
- **Searching** (`mem_search.py`, no model): after reading the user's message, the agent picks a few groups from the keyword table → `mem_search.py` does a literal search for every spelling in those groups → it prints the most relevant passages → the agent opens and reads those passages before answering.
- **The keyword table is generated and never edited by hand**; if the table is wrong, fix the semantic file or rule file and rebuild. **Rebuild after the weekly extraction day has finished extracting into the semantic layer**, once a week: semantic files and rule files normally change only on that day. Measured on one agent with 52 semantic files and 83 rule files: a rebuild takes about half an hour, a search about 0.1 second.
- The models and packages are installed in the user's home directory, not in the repo. They are the only third-party dependency, and only these two tools need them.
- **Status: the structure is decided, but the two tools are not in this kit yet.** The quality of the keyword table has not passed, and `mem_search.py` does not yet expand a group into its spellings. They ship once they pass and are tested, and only then does the rule "Finding something in the semantic layer" change to read the table first and then search; until then, follow that rule and find files from the list.
