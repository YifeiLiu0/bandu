# Input contract and context assembly

## Supported hierarchy

```text
book
  chapters[]
    sections[]
      beats[]
      subsections[]
        beats[]
```

A section may contain direct beats, subsection beats, or both. Never move beats or synthesize a subsection.

## Required source fields

Require:

- Root: `status`, `document_id`, `book`.
- Book: `id`, `chapters`; allow `title`, `summary`, `function`, and `flow` to be absent or null for a partial-book artifact.
- Chapter: `id`, `title`, `summary`, `function`, `flow`, `sections`.
- Section: `id`, `title`, `summary`, `function`, `flow`, `subsections`, `beats`.
- Subsection: `id`, `title`, `summary`, `function`, `flow`, `beats`.
- Beat: `id`, `title`, `summary`, `function`, `source_markdown`.

Do not repair or infer missing IDs, hierarchy, source bodies, or beat summaries.

## Structural context

For each book/chapter/section/subsection assemble:

```text
current summary/function/flow
+ parent summary/function/flow when available
+ immediate previous and next sibling summary/function
+ ordered child summaries/functions
```

At book level, use chapter rollups as provisional context when book rollups are missing. Identify the first two eligible direct children; a structural plan may promise only a payoff one of them can begin delivering.

Use compact evidence references such as `{"node_id":"c01-s01","field":"summary"}`. Do not paste source bodies into analysis fields.

## Beat context

For each beat assemble:

```text
current title/summary/function/source_markdown/artifact flags
+ immediate previous sibling metadata
+ next two sibling title/summary/function metadata
+ containing subsection, section, and chapter rollups
```

Sibling beats belong to the same direct `beats[]` array. Do not bridge across section or subsection boundaries.

Use only the current beat's `source_markdown`. Future sibling evidence is limited to `title`, `summary`, and `function`. A next dependency must point to the immediate next sibling; its closing checkpoint may point to that sibling or the second next sibling.

Treat bilingual paragraphs as one semantic source. Do not duplicate analysis by language unless requested.
