---
name: pre-analysis
description: Add source-grounded structural conflicts, structural commentary plans, beat difficulty assessments, and beat commentary plans to hierarchical book-segmentation JSON without changing existing data or formatting. Use when preparing book/chapter/section/subsection/beat JSON for a later commentary-writing pass, especially when extracting Pipeline A steps A1-A2 and Pipeline B steps B1-B2 from book-commentary into one enriched pre-analysis file.
---

# Pre-analysis

Enrich one segmentation JSON in four ordered passes. Keep the source file untouched and deliver one enriched JSON whose only changes are the four inserted analysis fields.

## Required references

Read all three before generating analysis:

- Read [references/input-contract.md](references/input-contract.md) for hierarchy and context boundaries.
- Read [references/analysis-guidelines.md](references/analysis-guidelines.md) for conflict, difficulty, reward, loop, voice, and planning rules.
- Read [references/output-contract.md](references/output-contract.md) for exact embedded field shapes and placement.

## Input and output gate

Accept one readable JSON file rooted at `book.chapters[]`. Default to Chinese analysis unless the caller requests another language.

Do not overwrite the input. Unless the caller supplies an output path, create `<input-stem>.pre-analysis.json` beside it. For `data/chapter1-segmentation.json`, output `data/chapter1-segmentation.pre-analysis.json`.

The final file must preserve every original value, key, array item, key order, array order, whitespace choice, and source location. Add only:

- `conflict`, then structural `plan`, immediately after `flow` on chapter/section/subsection nodes;
- `conflict`, then structural `plan`, immediately before `chapters` when a partial book lacks `flow`;
- `difficulty`, then beat `plan`, immediately after `function` on beat nodes.

Use the English key `difficulty`; “难点” describes its purpose, while the existing contract names the field `difficulty`.

## Working discipline

Generate each stage as a temporary patch envelope matching `output-contract.md`. The patch is not a deliverable. Apply it with the bundled script so the working JSON remains the previous step plus one new field:

```bash
python3 .claude/skills/pre-analysis/scripts/apply_stage.py <working.json> <stage-patch.json> --output <working.json>
```

For A1, pass the untouched source as `<working.json>` and the new enriched path as `--output`. For A2, B1, and B2, use the enriched path for both arguments. The script rejects missing, extra, duplicate, or already-annotated targets.

After every step validate against the original:

```bash
python3 .claude/skills/pre-analysis/scripts/validate_pre_analysis.py <original.json> <enriched.json> --through <1|2|3|4>
```

Delete temporary patch envelopes after the corresponding field has been applied and validated. Deliver only the enriched JSON.

## Pipeline A: structural units

Process `book`, `chapter`, `section`, and `subsection` nodes in source order.

### A1. Analyze conflict

Use current metadata, parent purpose, child flow, and adjacent sibling summaries/functions. Identify a reader-centered tension grounded in the source. Do not fabricate drama or use future source bodies. Use a provisional conflict for incomplete book context. Use `null` for non-expository references/assets instead of inventing tension.

Create a `unit_conflicts` patch containing every structural target exactly once. Apply it to insert each item's inner `conflict` value, then validate with `--through 1`.

### A2. Plan structural commentary

For every non-null conflict:

1. Choose one `hook_function` and an exact `promised_payoff`.
2. Point `payoff_checkpoint_id` to one of the first two eligible direct children that can begin delivering the promise; narrow unsupported promises.
3. Choose one healthy `emotional_target` and one `closing_function`.
4. Plan reader change, opening/closing angles, one structural voice, tone, factual boundary, forbidden moves, and maximum lengths.
5. Choose one source-fitting `presentation_form`, explain it in `form_rationale`, and map an analogy only when useful.

Create a `unit_plans` patch containing every structural target exactly once. Use `plan: null` wherever `conflict` is null. Apply only each item's inner `plan` value, then validate with `--through 2`.

## Pipeline B: beats

Process every beat in source order. Use the current beat body, its immediate previous sibling, the next two siblings' title/summary/function metadata, and containing rollups. Never read future `source_markdown`.

### B1. Assess difficulty

Score all five rubric dimensions from 0 to 2. Sum them and classify `simple` (0-3), `medium` (4-6), or `hard` (7-10). Explain the overall friction in `rationale`, list each concrete friction as a labeled `difficulty_points` entry with evidence, and always record a source-grounded `interest_seed`.

Create a `beat_difficulties` patch containing every beat exactly once. Apply each item's inner `difficulty` value, then validate with `--through 3`.

### B2. Plan beat commentary

For every beat:

1. Copy the exact difficulty labels this plan addresses into `target_difficulty_labels`, then complete one shared cognitive brief: old belief, central question, tension, information turn, payoff, emotional target, optional next dependency, function tags, and forbidden exaggeration.
2. Default the loop to `close`. Use `close_and_open` only for a real dependency on the immediate next sibling, with a closing checkpoint no later than the second next sibling in the same `beats[]` array.
3. Use `fun_brief` for simple beats and `fun_explanation` for medium/hard beats.
4. Select `mentor`, `student`, or both by source fit, never mechanically from difficulty. Keep at least one voice per beat and audit each chapter toward at least 70 percent coverage for each voice without padding.
5. When paired, define complementary jobs first. Then give every voice its own type, contribution, strategy, delivery design, presentation form, analogy decision, tone, and maximum length.

Draft all beat plans for a chapter, then run the chapter plan audit and concept-ownership checks from `analysis-guidelines.md` and rebalance failing drafts before patching.

Create a `beat_plans` patch containing every beat exactly once. Apply each item's inner `plan` value, then validate with `--through 4`.

## Completion gate

Run full validation with `--through 4`. Fail completion if any original content changed, any analysis field is misplaced, any target is absent, or any stage contradicts its upstream field. Do not emit separate `01`-`05` analysis artifacts as final outputs.
