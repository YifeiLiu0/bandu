# Input contract and context assembly

## Supported hierarchy

Traverse this logical hierarchy:

```text
book
  chapters[]
    sections[]
      beats[]
      subsections[]
        beats[]
```

A section may contain direct beats, subsection beats, or both. Do not assume `subsections[]` is non-empty. Do not move direct section beats into a synthetic subsection.

## Required source fields

Require:

- Root: `status`, `document_id`, `book`.
- Book: `id`, `chapters`.
- Chapter: `id`, `title`, `summary`, `function`, `flow`, `sections`.
- Section: `id`, `title`, `summary`, `function`, `flow`, `subsections`, `beats`.
- Subsection when present: `id`, `title`, `summary`, `function`, `flow`, `beats`.
- Beat: `id`, `title`, `summary`, `function`, `source_markdown`.

Allow book-level `title`, `summary`, `function`, and `flow` to be `null` or absent for partial-book artifacts. Never invent a missing title.

## Structural-unit context

For each book/chapter/section/subsection, assemble:

```text
identity
+ current summary/function/flow
+ parent summary/function/flow when available
+ immediate previous sibling summary/function
+ immediate next sibling summary/function
+ ordered child summaries/functions
```

Use only immediate siblings. Child rollups establish what the current unit can actually deliver. At book level, use chapter rollups as provisional context when the book rollup is absent.

For schema `0.5.0` and later, also identify the first two eligible direct children in source order. A unit opening may promise only a payoff supported by the unit, and its `payoff_checkpoint_id` must point to one of those first two children. This keeps the first understanding reward near the opening without requiring the hook to reveal the answer. If a unit has no eligible child that can deliver the promise, narrow the hook or skip the unit instead of inventing a checkpoint.

Record evidence as references such as:

```json
{"node_id": "c01-s01", "field": "summary"}
```

Do not paste entire source bodies into `context_used` or `evidence_refs`.

## Beat context

For each beat, assemble:

```text
current beat title/summary/function/source_markdown/artifact flags
+ immediate previous sibling beat title/summary/function
+ first and second next sibling beat title/summary/function when present
+ containing subsection summary/function/flow when present
+ containing section summary/function/flow
+ containing chapter summary/function/flow
```

Sibling beats are beats in the same direct `beats[]` array. Do not treat the last beat of one section as the previous sibling of the first beat of another section.

Use `source_markdown` to assess actual cognitive difficulty. Use rollups to understand why the beat appears here. Do not assess difficulty from summary length alone.

### Cognitive-reward context

For schema `0.5.0` and later, derive the beat brief from evidence in this order:

1. Use the current beat to identify the likely old belief, central question, tension, information turn, and payoff.
2. Use the containing rollups to explain why that payoff matters in the local flow.
3. Use the immediate next sibling's `summary` and `function` to decide whether a real `next_dependency` exists.
4. Use the second next sibling's `summary` and `function` only to set and support the latest allowed `close_by_target_id` for an opened loop.

Do not read a future beat's `source_markdown` to make the current comment more dramatic or specific. A bridge may name the next grounded question or dependency, but must not reveal the future beat's answer.

Treat `next_dependency` as optional. Set it to `null` when the next beat merely continues the topic, repeats the current point, starts a new example without a conceptual dependency, or cannot be described without unsupported inference. For schema `0.6.0`, also record the specific `reader_need` created by the current payoff and `why_current_stops` without answering it; both must be supported by the current beat and containing context. Never bridge across direct `beats[]` arrays; the last beat under a section or subsection has no beat-level next dependency.

Record cognitive-reward evidence with compact references such as:

```json
{"node_id": "c01-s01-b02", "field": "summary"}
```

Allowed future evidence fields are `title`, `summary`, and `function`. `next_dependency.evidence_refs` must point to the immediate next sibling; `loop_contract.close_by_evidence_refs` must point to its selected immediate or second-next checkpoint. The current beat may additionally cite `source_markdown`. Keep the brief concise; do not copy full source passages into planning artifacts.

For schema `0.6.0`, derive `delivery_design` only after the cognitive brief is stable. Ground `human_anchor` and every non-`none` lively turn in the current beat or recorded containing context. The `reader_reaction` may express a plausible beginner response, but must not invent a technical claim, emotion, profession, or failure unsupported by the available context.

## Source-specific observations for the MVP fixture

For `data/chapter1-segmentation.json`:

- Expect 1 book, 1 chapter, 9 sections, 0 subsections, and 29 beats.
- Expect 11 structural-unit records per structural stage: 1 book + 1 chapter + 9 sections.
- Expect 29 records per beat stage.
- Mark book-level context partial because its summary/function/flow are absent.
- Treat section `c01-s09` (`function: references`) as a skip record in structural stages.
- Preserve bilingual content as one semantic beat and generate Chinese commentary by default.
