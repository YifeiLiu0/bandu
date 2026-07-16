# Enriched input contract

## Hierarchy

Traverse without moving or synthesizing nodes:

```text
book
  chapters[]
    sections[]
      beats[]
      subsections[]
        beats[]
```

A section may contain direct beats, subsection beats, or both.

## Source fields

Require root `status`, `document_id`, and `book`.

Require:

- Book: `id`, `chapters`; allow missing/null `title`, `summary`, `function`, or `flow` for a partial-book artifact.
- Chapter: `id`, `title`, `summary`, `function`, `flow`, `sections`.
- Section: `id`, `title`, `summary`, `function`, `flow`, `subsections`, `beats`.
- Subsection: `id`, `title`, `summary`, `function`, `flow`, `beats`.
- Beat: `id`, `title`, `summary`, `function`, `source_markdown`.

Preserve all IDs, source order, hierarchy, and source text.

## Structural writing brief

Require every book/chapter/section/subsection to contain:

- `conflict`: null or an object containing `type`, `reader_assumption`, `counterforce`, `stakes`, `open_loop`, `statement`, `evidence_refs`, and `confidence`.
- `plan`: null or an object containing reader-state goals, opening/closing angles, one voice, presentation form and rationale, analogy decision, reward design, tone tags, and constraints.

Require both fields to be null together or non-null together. Treat null as a skipped non-expository unit and omit that node from the final commentary document.

Do not rewrite the conflict or plan during A3. Read child/sibling metadata only to verify that the planned promise and checkpoint remain grounded.

## Beat writing brief

Require every beat to contain:

- `difficulty`: five scored dimensions, total score, level, rationale, labeled difficulty points, and interest seed.
- `plan`: mode, primary goal, targeted difficulty labels, angle, commentary brief, loop contract, optional pairing design, and one or two voice-specific comment plans.

Require every target difficulty label to exist in `difficulty.difficulty_points`. Require comment plan voice order to be `mentor`, `student`, or `mentor` then `student`. Lock mentor to `fun_commentary` and student to `roast`.

During B3, read the current beat's `source_markdown` to verify accuracy. Do not read a future beat's body. The embedded next dependency and closing checkpoint may refer only to the next two siblings in the same direct `beats[]` array.

## Source metadata for the artifact

Copy `document_id`, `source_path`, and `source_sha256` from the enriched input into the one output envelope. Use null for an unavailable optional source field; never invent it.
