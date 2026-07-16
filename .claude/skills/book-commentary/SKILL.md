---
name: book-commentary
description: Write reader-facing structural hooks, closing questions, mentor explanations, and student roasts from hierarchical book-segmentation JSON already enriched by pre-analysis with structural conflict/plan and beat difficulty/plan fields. Use when completing only commentary-writing steps A3 and B3 for professional or educational books, honoring the embedded analysis as a binding brief, and producing one source-ordered JSON containing only final commentary plus target IDs and unit types.
---

# Book Commentary

Turn a `$pre-analysis` enriched segmentation JSON into beginner-friendly commentary. Perform only structural writing step A3 and beat writing step B3. Do not regenerate or revise conflicts, difficulties, plans, or source content.

## Required references

Read all three references before writing:

- Read [references/input-contract.md](references/input-contract.md) to validate and traverse the enriched input.
- Read [references/commentary-guidelines.md](references/commentary-guidelines.md) for A3/B3 prose and acceptance rules.
- Read [references/output-contracts.md](references/output-contracts.md) for the single final-commentary artifact.

## Input gate

Accept one readable JSON rooted at `book.chapters[]`. Require:

- every book/chapter/section/subsection node to contain adjacent `conflict` and structural `plan` fields;
- every beat to contain adjacent `difficulty` and beat `plan` fields;
- structural `conflict` and `plan` to be null together only for skipped non-expository units;
- every beat plan to contain one or two voice-specific `comment_plans`.

Validate before writing:

```bash
python3 .claude/skills/book-commentary/scripts/validate_commentary.py <pre-analysis.json>
```

Stop on validation errors. Do not repair, complete, or reinterpret an invalid upstream analysis. Return to `$pre-analysis` when the conflict, difficulty, payoff, loop, voice set, form, analogy, or length budget prevents passing prose.

## Output location and invariants

Use an explicitly requested output path. Otherwise strip a trailing `.pre-analysis` from the input stem and create `<base-stem>.commentary.json` beside it. For `chapter1-segmentation.pre-analysis.json`, write `chapter1-segmentation.commentary.json`.

Write exactly one JSON document with `schema_version: "0.7.0"` and `stage: "book_commentary"`. Default to Chinese (`zh-CN`) unless requested otherwise. Treat bilingual source paragraphs as one semantic source.

Keep only final reader-facing commentary plus `target_id` and `unit_type` for locating it. Do not copy titles, summaries, functions, flows, source bodies, conflicts, difficulties, plans, upstream links, reward metadata, contributions, pair checks, self-checks, or skipped structural nodes into the output.

Interleave eligible structural and beat commentary in source traversal order:

```text
book -> chapter -> section -> its direct beats -> subsection -> its beats -> next section
```

Generate one opening hook and one closing question for every non-skipped structural node. Generate exactly one commentary for every entry in each beat's `comment_plans`, preserving planned voice order. Keep A3 results in memory until B3 completes, then write the single document once. Do not overwrite the enriched input.

When converting an existing two-artifact run without rewriting its prose, merge and strip it with:

```bash
python3 .claude/skills/book-commentary/scripts/merge_commentary.py <pre-analysis.json> <unit-comments.json> <beat-comments.json> --output <commentary.json>
```

## Pipeline A: structural units

Process book, chapter, section, and subsection nodes in source order.

### A3. Write a story-like hook and question

Treat the node's `conflict` and structural `plan` as a binding brief. Silently map:

```text
reader_assumption + counterforce -> visible collision
stakes + open_loop -> reason to want the answer
primary_goal + reader_after -> closing question's job
angles + voice + tone + constraints -> delivery
presentation_form + analogy -> visible shape
reward_design -> early reward contract and intended landing
```

For every non-skipped unit:

1. Build a zero-background hook around the exact conflict. Name a precise knowledge question, preserve its answer, and promise only what the planned early checkpoint can begin paying off.
2. Realize the planned presentation form. Use a core question, contrast, brief exchange, scene, bullets, or arrows only when that shape reveals the collision faster than a paragraph.
3. Use short spoken sentences, concrete subjects, and visible actions. Use an analogy only when planned and preserve its exact mapping.
4. Remove taxonomy labels, abstract-noun chains, formal recap language, teacherly prompts, and pseudo-dialogue that merely splits a definition.
5. Write a closing question that performs the planned exit function. Make it a natural next move, not a school quiz. Keep it answerable within the unit unless the plan explicitly supports reflection or a forward bridge.
6. Compare the draft against every conflict/plan field and all applicable acceptance tests. Reject unsupported promises, late payoffs, fake curiosity, generic continuation, or compressed-lesson prose.

Keep only the selected `opening_hook` and `closing_question` in the final structural item. Run self-checks privately; do not emit them. Emit no item for a skipped node.

## Pipeline B: beats

Process every beat in source order. Read only the current beat's `source_markdown`; use future sibling metadata solely through the embedded plan.

### B3. Write one or two voice-locked beat comments

Treat `difficulty` and beat `plan` as a binding brief. Do not start from the source summary alone. Complete these silent passes for each planned voice:

1. Build the payoff skeleton without humor, analogy, formatting, or teaser language.
2. Move from the planned old belief through tension and information turn to the exact payoff; remove every step that does not serve the one cognitive job.
3. Realize the voice-specific human entry, strategy, lively turn, presentation form, and analogy. Sound like a smart reading companion beside the reader.
4. Deliver the current payoff before any bridge. Only a planned mentor may add a `close_and_open` bridge. End student text on its roast or plain-language verdict.
5. Hide the planning scaffold. Replace labels and abstractions with actors, objects, actions, causal links, distinctions, and consequences.
6. Compress into spoken language. Use at most one planned comic/narrative device or analogy; stop when the payoff or grounded bridge lands.

Keep a private chapter-level style ledger while writing. Track recent voice, form, opening pattern, device, analogy domain, roast target, landing, and core claim. Re-audit repeated forms, adjacent open loops, weak voice differentiation, and chapter voice coverage; never emit the ledger.

- For `student`, emit only `comment_type: "roast"`. Roast a source-specific situation, system behavior, inflated promise, or harmless first impulse—never the reader. Reject movable complaints, miniature lessons, study questions, and recurring first-person scaffolds.
- For `mentor`, emit only `comment_type: "fun_commentary"`. Bridge the missing reasoning step in plain language and land on the exact source concept. Avoid taxonomy-first or documentation-style prose.
- For simple beats, build from `interest_seed`; for medium/hard beats, resolve the labeled difficulty points targeted by the plan.
- Emit one text per planned voice in identical order. In a pair, mentor clarifies the mechanism while student makes the mismatch recognizable or memorable; neither paraphrases the other.

Run all applicable B3 checks privately before accepting each commentary. In the final beat item, keep only each commentary's `voice`, `comment_type`, `presentation_form`, and `text`. After A3 and B3 are complete, write the one merged artifact and validate it:

```bash
python3 .claude/skills/book-commentary/scripts/validate_commentary.py <pre-analysis.json> --commentary <commentary.json>
```

## Generation discipline

- Finish and privately check A3 before B3; save only after both are complete.
- Write valid UTF-8 JSON, never JSON inside Markdown fences.
- Encode intentional line breaks as `\n`; use bullets or arrows only when required by the planned form.
- Preserve semantic strength, required terminology, factual boundaries, planned voice order, and maximum lengths.
- Deliver the planned current payoff before any grounded next-beat bridge.
- Fail rather than accepting prose that would make any required private self-check false.
- Optimize for understanding, accurate recall, return to the source, and recoverable chapter flow—not attention traps or endless continuation.

## Execution model

Use one agent for one chapter or up to 100 beats so A3 and B3 share the same interpretation and style ledger. For larger books, freeze shared voice rules, process by chapter, and run one final cross-chapter consistency pass.
