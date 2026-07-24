# Pre-analysis guidelines

## Product boundary

Plan for beginner understanding, fast cognitive payoff, accurate recall, and source-grounded continuation. Never trade accuracy for entertainment, fabricate author intent, blame the reader, withhold a current explanation to force continuation, or create a generic cliffhanger.

## Structural conflict

A conflict is a grounded tension between the reader's likely model or goal and the obstacle, counterintuitive fact, trade-off, or missing answer the unit addresses.

Choose one type:

- `expectation_vs_reality`
- `goal_vs_obstacle`
- `intuition_vs_mechanism`
- `old_model_vs_new_model`
- `simplicity_vs_reliability`
- `benefit_vs_cost`
- `question_vs_missing_answer`

Record `reader_assumption`, `counterforce`, `stakes`, `open_loop`, `statement`, compact `evidence_refs`, and `confidence` (`low`, `medium`, or `high`). Use `null` for pure references/assets. A conflict diagnoses tension; it is not reader-facing hook copy.

## Structural plan

Choose one primary goal:

- `create_curiosity`
- `surface_misconception`
- `make_stakes_concrete`
- `orient_in_flow`
- `prepare_for_conceptual_shift`
- `consolidate_and_transfer`

Choose one opening angle: `surprising question`, `familiar failure scenario`, `counterintuitive contrast`, `practical stakes`, or `unresolved consequence from the previous sibling`.

Choose one closing angle: `explain in the reader's own words`, `apply to a small scenario`, `distinguish two nearby concepts`, `diagnose a failure`, or `predict what changes next`.

Use one structural voice: `mentor` or `student`. Select one presentation form from `core_question`, `contrast_pair`, `mini_dialogue`, `scene_then_point`, `short_paragraph`, `arrow_chain`, or `bullet_breakdown`. Use arrows only for three to five meaningful nodes across at least two transitions; content needing more transitions must be planned as several short chains on separate lines, each ending on a nameable intermediate product. Use bullets only for genuinely parallel items.

Write every plan field that the writing pass will surface in reader-facing prose — `promised_payoff`, payoff statements, jobs, anchors, bridge questions — in words a zero-background reader could understand as-is. A compressed label like “迁移判断” fails; “什么时候值得把任务改成链” passes.

Plan one reward:

- Entry/hook function: `misconception`, `stakes`, `mystery`, `conflict`, `personal_relevance`.
- Emotional target: `surprise`, `relief`, `control`, `curiosity`, `vigilance`.
- Closing function: `payoff`, `mental_model`, `chapter_position`, `bridge`, `memory_anchor`.

State `promised_payoff` as the understanding or capability the unit delivers. Set `payoff_checkpoint_id` to one of the first two eligible direct children that can begin delivering it. Default Chinese limits are 90 characters for an opening and 60 for a question; use only maxima.

## Concept ownership and callbacks

While planning, keep a running chapter registry of payoff statements already assigned to earlier units and beats (this only looks backward, so it never violates the no-future-source rule). Before finalizing any payoff, check the registry:

- The first unit that teaches a concept owns its full explanation.
- When a later unit — especially a recap, diagram, or takeaway list — returns to an owned concept, its payoff must be typed `connection` and must name (a) a one-line callback to the owning unit and (b) the increment only this unit provides: the diagram's directionality, the ordering of the takeaways, a new linkage between known points. A plan that re-teaches an owned concept in full fails this check.

## Difficulty rubric

Score every dimension from 0 to 2:

- `abstraction`: concrete (0), mixed (1), abstract/meta (2).
- `prerequisite_load`: common knowledge (0), one assumed concept (1), several specialized prerequisites (2).
- `reasoning_gap`: explicit transition (0), one implicit step (1), multiple/non-obvious steps (2).
- `terminology_density`: ordinary language (0), some domain terms (1), dense/confusable terms (2).
- `representation_complexity`: plain prose (0), list/simple structure (1), code/JSON/table/diagram/multipart artifact (2).

The sum determines `simple` (0-3), `medium` (4-6), or `hard` (7-10). Long text or an artifact flag alone does not make a beat hard. Summarize the classification in `rationale`. Then record every concrete friction in `difficulty_points` with a stable snake-case `label`, a reader-centered `reader_friction`, and compact source `evidence`. Always add a small useful implication, connection, or surprise as `interest_seed`.

## Cognitive brief and payoff

Start every beat plan with `target_difficulty_labels`: copy the labels of the difficulty points the plan explicitly addresses. An empty array is allowed only when a simple beat has no substantive friction beyond its interest seed.

Plan one minimum change in understanding:

```text
reader_old_belief -> tension -> information_turn -> payoff
```

Choose one payoff type:

- `understanding`
- `judgment`
- `action`
- `misconception_correction`
- `connection`

Scope every payoff to the current beat: the statement must be recoverable from this beat's source plus already-read context alone. When the natural judgment belongs to a later sibling — visible from its title, summary, or function metadata — narrow the current payoff to what this beat establishes and leave that judgment to the owning beat; the owning beat's plan may call back to this one. Check each payoff against the chapter registry in “Concept ownership and callbacks”.

Use the same emotional-target enum as structural plans. Choose function tags from:

- Entry: `misconception`, `stakes`, `mystery`, `conflict`, `personal_relevance`.
- Explanation: `analogy`, `personification`, `mini_scene`, `counterexample`, `contrast`, `missing_prerequisite`, `author_intent`, `source_trace`, or `null`.
- Exit: `payoff`, `mental_model`, `chapter_position`, `bridge`, `memory_anchor`.

Record specific claim-strength, causality, intent, and spoiler errors under `forbidden_exaggeration`. Each entry is a silent guardrail for the writing pass, never content to surface: it names one overstatement of a claim actually present in the current beat's source, phrased as “不要把 X 说成/保证/等同于 Y”. An entry that directs content in (“不要忽略 X”, “要提到 X”) or that bans a claim the source never makes fails this check — cut it or reground it. Vary entries by what this beat actually risks; do not stamp the same boundary reminder onto every beat.

## Loop policy

Default to `loop_contract.action: close`. Use `close_and_open` only when all are true:

1. The current payoff creates a specific reader need.
2. The current beat cannot answer it honestly.
3. The immediate next sibling directly addresses it in `summary` or `function`.
4. The loop clarifies a knowledge dependency rather than varying the ending.

For `close_and_open`, record `next_dependency.target_id`, `relationship`, `reader_need`, `why_current_stops`, `bridge_question`, and evidence. Copy the exact bridge question to `loop_contract.next_question`. Set `close_by_target_id` to the immediate or second next sibling in the same direct array. Otherwise keep the dependency and all checkpoint fields null and evidence empty.

## Voice and delivery planning

Difficulty selects mode: `fun_brief` for simple and `fun_explanation` for medium/hard. It does not select voice.

- Include `mentor` when the payoff needs a reasoning bridge. Lock its type to `fun_commentary` and `roast_move` to null.
- Include `student` for a source-specific mismatch, false confidence, overengineering move, awkward consequence, empty abstraction, or plain-language realization. Lock its type to `roast` and choose `promise_vs_reality`, `literal_consequence`, `role_personification`, `everyday_mapping`, `deadpan_relabeling`, or `dialogue_snap`.

Select at least one voice per beat. Within each chapter, target at least 70 percent coverage for each voice where honest source-grounded contributions exist. Never pad coverage with a movable joke or redundant explanation. A `close_and_open` plan must include mentor; student never carries a bridge or study question.

For paired voices, define `mentor_job`, `student_job`, and `non_overlap` before planning either delivery. Give each voice its own `human_anchor`; identical anchors fail. Any analogy, metaphor, or image named in one voice's job belongs to that voice alone — record the ownership in `non_overlap` so the other voice cannot borrow it. Reject pairs whose landings answer the same question in near-identical words.

Choose one strategy per voice. For `fun_explanation`: `concrete_analogy`, `micro_scenario`, `step_by_step_bridge`, `contrast_pair`, `misconception_correction`, or `plain_language_reframe`. For `fun_brief`: `light_observation`, `useful_connection`, `reader_reaction`, `small_surprise`, or `gentle_wit`.

For each voice record:

- one source-grounded `human_anchor`;
- one plausible `reader_reaction`;
- at most one lively device: `micro_scene`, `inner_monologue`, `role_dialogue`, `consequence_zoom`, `plainspoken_reframe`, or `none`;
- one presentation form and source-specific rationale;
- an analogy only with an exact source mapping;
- tone tags, must/avoid constraints, and only `max_chars`.

Default Chinese maxima: student simple 65, student medium/hard 90, mentor simple 90, mentor medium 150, mentor hard 200. Shorter passing plans are preferable to padding.

## Chapter plan audit

After drafting every beat plan in a chapter and before emitting the `beat_plans` patch, audit the drafts as one distribution per voice:

- one `presentation_form` holds at most one third of a voice's plans and never runs three beats in a row;
- one `strategy` holds at most half of a voice's plans;
- one entry tag and one exit tag each hold at most about half of the chapter's beat plans.

For each plan past a cap, pick the next-best form or strategy that still fits its source and record the source fit in the rationale — rebalancing never licenses a form the beat cannot support. A chapter whose source genuinely forces a cap violation keeps the plan and notes why in `form_rationale`; silent overruns fail the audit. Rerun the concept-ownership registry check across the finished chapter at the same time.
