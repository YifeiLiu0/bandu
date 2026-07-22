---
name: book-commentary-old
description: Generate staged, grounded commentary JSON from hierarchical book-segmentation JSON containing book, chapter, section, optional subsection, and beat nodes. Use when turning professional or educational books into beginner-friendly reading with low cognitive-reward latency through structural conflicts, precise curiosity hooks, early payoffs, grounded next-beat bridges, difficulty analysis, plain-language explanations, and light witty reactions, while preserving source IDs and saving every analysis stage as a separate JSON artifact.
---

# Book Commentary

Turn segmented professional-book content into commentary that helps readers understand the material, regain cognitive confidence, and continue for a real knowledge reason. Reduce reward latency: surface the exact knowledge conflict early, deliver one useful payoff per eligible beat, and open another question only when the source contains a grounded dependency. Run two independent three-stage pipelines: structural commentary for book/chapter/section/subsection units, and local commentary for beats. Structural units use one selected voice. Every beat uses at least one reader-facing voice and may pair a `mentor` explanation with a complementary `student` roast.

## Required references

Read all three references before generating artifacts:

- Read [references/input-contract.md](references/input-contract.md) to traverse nodes and assemble local context.
- Read [references/commentary-guidelines.md](references/commentary-guidelines.md) to assess conflicts, difficulty, voice, and quality.
- Read [references/output-contracts.md](references/output-contracts.md) to write the six JSON artifacts.

## Input gate

Accept one readable JSON file whose root contains `book.chapters[]`, with `sections[]` under every chapter and `beats[]` either directly under a section or under `subsections[]`.

Validate before generation:

```bash
python3 .claude/skills/book-commentary-old/scripts/validate_commentary.py <segmentation.json>
```

Stop on validation errors. Do not silently repair IDs, source text, hierarchy, or missing beat summaries. Allow missing book-level `summary`, `function`, or `flow`; derive only a provisional book-level conflict from available chapter rollups and record the missing fields.

## Output location and invariants

Use an explicitly requested output directory. Otherwise create a sibling directory named `<input-stem>.commentary`. For `data/chapter1-segmentation.json`, use `data/chapter1-segmentation.commentary/`.

Always preserve source IDs and source order. Record every eligible and skipped target exactly once. Treat `references`, `asset_reference`, and other non-expository units as skipped instead of inventing dramatic tension.

Default to Chinese commentary (`zh-CN`) unless the caller requests another language. Treat bilingual source paragraphs as one semantic source; do not repeat the comment in two languages unless requested.

Generate one reader-facing opening hook and closing question per eligible structural target. Select one structural voice in the planning stage.

Generate one or two reader-facing comments per beat. Every beat must contain at least one of `mentor` or `student`; the two voices may appear together when they perform different jobs. Within each chapter, target at least 70 percent beat coverage for each voice. Treat full beat coverage as a hard invariant and the per-voice targets as a generation and final-review requirement: re-audit voice-fit decisions instead of padding weak comments merely to satisfy a quota.

Generate new artifacts with `schema_version: "0.7.0"`. Preserve the existing six-file sequence. Version 0.7 keeps the shared beat-level cognitive brief and adds one or two voice-specific comment plans and outputs so both voices can coexist without duplicating one another. Keep legacy `0.1.0` through `0.6.0` artifacts valid; do not write new runs with a legacy schema.

## Pipeline A: structural units

Process `book`, `chapter`, `section`, and `subsection` nodes in source order.

### A1. Analyze conflict

Use current metadata, parent purpose, child flow, and adjacent sibling summaries/functions. Identify a reader-centered tension grounded in the source, not fabricated drama. Save immediately as:

```text
01-unit-conflicts.json
```

For incomplete book context, use `eligibility: "provisional"`. For non-expository units, use `eligibility: "skip"` with a reason. Do not use future source content beyond summaries/functions/flows.

Validate before continuing:

```bash
python3 .claude/skills/book-commentary-old/scripts/validate_commentary.py <segmentation.json> --artifacts-dir <output-dir> --through 1
```

### A2. Plan structural commentary

For each non-skipped conflict, plan the reader-state change and early reward before choosing delivery:

1. Choose one entry-function `hook_function` and state the exact `promised_payoff` the unit can deliver.
2. Set `payoff_checkpoint_id` to one of the first two eligible direct children that can begin delivering that promise. Narrow the promise when neither early child supports it.
3. Choose one healthy `emotional_target` and one exit-function `closing_function` from `commentary-guidelines.md`.
4. Decide the opening and closing angles, voice, tone, factual boundary, forbidden moves, and maximum lengths.
5. Choose one source-fitting `presentation_form` for the opening and record a `form_rationale` explaining which source relationship the form makes easier to see. Record whether an analogy is useful and, when it is, its domain and exact source mapping.

Base every field on A1 and recorded source context. Save immediately as:

```text
02-unit-plans.json
```

Validate with `--through 2` before continuing.

### A3. Write a story-like hook and question

Read both A1 and A2 as a binding brief, not loose inspiration. Before drafting, silently map:

```text
reader_assumption + counterforce -> the hook's visible collision
stakes + open_loop -> why the reader wants the answer
primary_goal + reader_after -> the closing question's job
opening/closing angles + voice + tone + constraints -> delivery
presentation_form + analogy decision -> the hook's visible shape
hook_function + promised_payoff + payoff_checkpoint -> the early reward contract
emotional_target + closing_function -> the intended reader landing
```

For every non-skipped unit:

1. Build a zero-background hook around the exact collision from A1. Name a precise knowledge question, preserve its answer, and promise only what the planned early checkpoint can begin paying off.
2. Realize the planned `presentation_form`. Use line breaks, a core question, a contrast, a brief exchange, bullets, or arrows only when that form exposes the conflict faster than a paragraph.
3. Rewrite in short, spoken sentences with concrete subjects and verbs. Keep each sentence to one job and each paragraph to one or two sentences. Use an analogy only when A2 planned one; map it cleanly and keep the answer hidden.
4. Remove the lecture scaffold. Replace taxonomy labels and abstract-noun chains with a visible collision between a person, role, object, action, or result. Delete formal recap language and pseudo-dialogue that merely splits a definition between speakers. Preserve necessary source terms and the exact promise.
5. Write a closing question that performs the planned exit function and feels like the next move in the story, not a school quiz. Ask the reader to diagnose a tiny scenario, choose between two nearby ideas, recover a mental model, or bridge to a supported dependency. Keep it answerable from the current unit unless explicitly marked as reflection.
6. Compare the draft against every A1/A2 field and all structural reward, readability, companion-voice, lecture-scaffold, form, spoken-language, and analogy tests. Reject hooks that promise a late or unsupported payoff, withhold the current answer for continuation, create curiosity without a knowledge dependency, or sound like a compressed lesson.

Emit only the selected hook and question, not the private mapping or rejected drafts. Copy the four planned structural reward fields into `reward_delivery` and set the v0.5 structural self-checks only after verifying the promise, checkpoint, and healthy continuation. Save immediately as:

```text
03-unit-comments.json
```

Validate with `--through 3` before continuing.

## Pipeline B: beats

Process every beat in source order. Use the current beat body, its immediate previous sibling, the next two siblings' title/summary/function metadata, and its containing section/subsection and chapter rollups. Never read future `source_markdown` to improve the current hook or bridge.

### B1. Assess difficulty

Score the five rubric dimensions in `commentary-guidelines.md`. Classify each beat as `simple`, `medium`, or `hard`. Use `rationale` to explain the classification and identify the concrete reader friction evidenced by the beat. For `simple`, identify an `interest_seed` for a light comment. Record the exact previous, next, and second-next sibling IDs, using `null` at array boundaries. Save immediately as:

```text
04-beat-difficulties.json
```

Validate with `--through 4` before continuing.

### B2. Plan beat commentary

Create a plan for every beat in this order:

1. Complete `commentary_brief`: record `reader_old_belief`, `central_question`, `tension`, `information_turn`, one `payoff` type and statement, one healthy `emotional_target`, optional `next_dependency`, entry/explanation/exit function tags, and explicit `forbidden_exaggeration`.
2. Make the payoff describe what the reader can understand, judge, do, correct, or connect now. Do not use humor, format, or continuation as the payoff.
3. Set `loop_contract.action: close` by default. Use `close_and_open` only when the current payoff creates a specific reader need that the current beat cannot answer and the immediate next sibling directly addresses. Record `reader_need` and `why_current_stops`, cite the next beat's metadata, copy the precise bridge question, and choose that sibling or the second next sibling as the evidenced closing checkpoint. Mere topic continuation, another example, or a convenient chapter transition is not a dependency. Never cross the direct `beats[]` array.
4. Use `fun_explanation` for `medium` or `hard` beats and target the reader friction recorded in B1 `rationale`. Use `fun_brief` for `simple` beats and illuminate the `interest_seed` without manufacturing difficulty.
5. Choose a voice set containing `mentor`, `student`, or both. Every beat must receive at least one voice. Include `mentor` when the payoff needs an explicit reasoning bridge. Include `student` when the beat contains a source-specific mismatch, false confidence, overengineering move, awkward consequence, empty abstraction, or plain-language realization that a sharp friend could roast without distorting the source. Do not map voice mechanically from difficulty.
6. When both voices are selected, complete `pairing_design` first. Give `mentor` the explanation job and `student` the plainspoken-roast job. State the distinct angle and landing for each voice. Reject a pair when the student text would only be a shortened, slangier, or first-person version of the mentor text.
7. Create one entry in `comment_plans` for every selected voice. Within each entry, complete `delivery_design`: ground one `human_anchor` in the beat, write one plausible reader-facing entry, and choose at most one `lively_turn` that reveals the source relationship. Use `device: "none"` when a light turn would be forced.
8. Record the voice-locked type in each comment plan: `student` -> `roast`; `mentor` -> `fun_commentary`. Choose one source-fitting strategy, presentation form, and optional analogy only after the shared cognitive brief and voice-specific delivery design are stable. Record `form_rationale`; use arrows only to trace at least three meaningful nodes across two transitions and bullets only for genuinely parallel source items.
9. Set only a maximum length for each comment plan from `commentary-guidelines.md`. Reserve space for a bridge only in a mentor plan and only after the current payoff fits. Student comments close on the roast or plain-language realization; they do not append a study question or generic continuation hook.

Choose one shared cognitive job for the beat. Treat each voice as a different delivery contribution to that job, not as an alternate answer. After planning a chapter, calculate coverage for both voices. Re-audit source-fitting student angles and mentor reasoning needs until both reach at least 70 percent where honest source-grounded comments are available; never fill a coverage gap with a movable complaint or redundant explanation. Save immediately as:

```text
05-beat-plans.json
```

Validate with `--through 5` before continuing.

### B3. Write one or two voice-locked beat comments

Read B1 and B2 as a binding brief. Do not start from the source summary alone.

Before writing the final text, complete six silent passes for each planned voice in order. Do not emit the drafts or pass notes:

1. **Build the payoff skeleton.** State the planned source-grounded payoff without analogy, humor, format, or teaser language. Identify the concrete action, causal link, distinction, correction, or connection the reader gains now.
2. **Create the cognitive turn.** Move from `reader_old_belief` through the exact `tension` and `information_turn` to that payoff. Remove any step that does not serve the single planned cognitive job.
3. **Realize entry, voice, and shape.** Use the current comment plan's `delivery_design`, function tags, voice, strategy, and `presentation_form`. Begin from the recorded human anchor or reader-facing entry, and realize the lively turn only when its planned device is not `none`. Establish the shared relationship first: sound like a smart reading companion beside the reader, not an instructor facing a class. Let bullets, arrows, contrast, dialogue, or a core question expose the relationship instead of repeating it in prose, but do not mistake compressed notation or first person for conversational voice.
4. **Close before opening.** Make the current payoff or voice-specific contribution visible first. Only a planned mentor comment may add the recorded `close_and_open` bridge after the payoff; keep the future answer hidden and do not introduce a second unsupported loop. End a student comment on its roast or plain-language turn.
5. **Remove the lecture scaffold.** Hide the planning skeleton after it has done its job. Replace taxonomy labels, abstract-noun chains, and colon-led definitions with actors, objects, actions, and consequences. Remove formal recaps, teacherly prompts, and pseudo-dialogue that merely assigns a definition to two speakers. Preserve necessary source terms and semantic strength.
6. **Make it spoken, light, and compressed.** Replace remaining abstractions with everyday syntax and observable verbs. Use at most one source-bound comic or narrative device or planned analogy. Split overloaded sentences, remove duplicate explanation, and stop when the payoff or grounded bridge lands.

Reject a draft when a later pass makes the payoff skeleton harder to recover. Accuracy and beginner clarity must survive the humor and compression passes.

Because beats are written in source order, keep a private chapter-level ledger. After accepting each comment, record voice, payoff contribution, emotional target, loop action, presentation form, line count, sentence-length shape, primary narrative/comic device, analogy domain if any, opening pattern, roast target, punchline/payoff shape, and core claim. Before drafting the next comment, inspect the previous three to five entries of the same voice and any paired comment on the current beat. Avoid repeating the same delivery combination when a source-fitting alternative exists, but never rotate payoff type, form, or humor mechanically. After planning and after writing the chapter, re-audit when either voice covers less than 70 percent of beats, schematic forms or opened bridges exceed roughly one third of eligible beats, one form appears three times consecutively, adjacent comments both open loops, or student comments repeatedly depend on `我以为`, `我想`, or `懂了` scaffolds. Treat style thresholds as review triggers; full beat coverage and final per-voice coverage are acceptance gates. Do not emit or save this ledger as an artifact.

- If `voice` is `student`, emit only `comment_type: "roast"`. Sound like a perceptive, funny, slightly sharp friend who spots the source-grounded absurdity and says it in ordinary language. Build from a concrete source cue through a mismatch or awkward consequence to a compact punchline, deadpan relabeling, or plainspoken verdict. First person is optional and never the mechanism that creates the voice. The roast must survive removing `我`; reject recurring `我以为……结果……懂了……` scaffolds, movable complaints, miniature lessons, and study questions. Roast the situation, system behavior, inflated promise, or harmless first impulse, never the reader's intelligence.
- If `voice` is `mentor`, emit only `comment_type: "fun_commentary"`. Turn the source idea into an enjoyable explanation: begin from a reader-recognizable action, result, predicament, or sharp contrast when the source supports one; expose the mistaken model; bridge the missing step in plain language; and land on the exact source concept. Sound like a smart friend leaning over to point out the interesting part. Do not open with a taxonomy, documentation label, or formal conclusion merely because it is concise.
- For a medium or hard mentor beat, spend only the space needed for the missing reasoning bridge. Prefer several short lines over one complete-looking paragraph; do not add terminology, repeated conclusions, or multiple analogies.
- For a simple beat, build from `interest_seed`; for a medium or hard beat, directly resolve the reader friction recorded in B1 `rationale`. Deliver the planned payoff type in either case. Use one primary comic or narrative device and reconnect it to the source.
- Assume zero background. Prefer everyday words, short sentences, and visible actions; explain an essential term inline on first use.
- Emit exactly one text for each entry in `comment_plans`, preserving planned voice order. Emit no unplanned alternate version or separate takeaway. When both voices are present, run a pair check: the mentor must make the mechanism easier to understand, the student must make the source-specific mismatch easier to recognize or remember, and neither may merely paraphrase the other.

Copy the shared planned reward fields into `reward_delivery` and record each voice's delivery contribution. Run every applicable B3 acceptance test in `commentary-guidelines.md`, including companion-voice, human-entry, lecture-scaffold, payoff, competence, loop/bridge, fake-cliffhanger, one-job, student-roast, and pair-complementarity tests, before setting `self_check`. Rewrite on any failure. Return to B2 when the payoff, loop, voice set, angle, form, delivery design, pairing, or length budget prevents a passing comment; do not save a completed item with knowingly false quality checks.

Never introduce analogy details that could be mistaken for claims in the book. Save immediately as:

```text
06-beat-comments.json
```

Validate the complete run:

```bash
python3 .claude/skills/book-commentary-old/scripts/validate_commentary.py <segmentation.json> --artifacts-dir <output-dir> --through 6
```

## Generation discipline

- Finish, save, and validate one stage before starting the next.
- Write valid UTF-8 JSON, not JSON inside Markdown fences.
- Keep each final voice comment in its own JSON `text` field inside the beat's `commentaries` collection. Encode intentional line breaks as `\n`; use bullets or `→` only when required by that voice's planned presentation form.
- Keep analysis fields concise and evidence-linked; do not copy full `source_markdown` into artifacts.
- Read only the current beat's `source_markdown`; use future sibling metadata solely for grounded dependency and checkpoint evidence.
- Use `null` and explicit missing-field lists instead of inventing unavailable context.
- Deliver one useful cognitive payoff per eligible beat. Close the current question before any grounded bridge, and never use an open-only or generic cliffhanger.
- Treat hooks, questions, roasts, and fun explanations as reader guidance, not source summaries or attention traps. A paired roast and explanation must be complementary, not two summaries of the same beat.
- Optimize for understanding, accurate recall, return to the source, and recoverable chapter flow rather than endless continuation or dwell time.
- Fail the stage when its upstream artifact is absent or invalid.
- Do not overwrite the segmentation input.

## MVP execution model

Use one agent for one chapter or up to 100 beats so all stages share the same interpretation. For larger books, first freeze shared context and voice rules, then parallelize by chapter; keep both voices and both pipelines together within each chapter, and run one final cross-chapter consistency pass.
