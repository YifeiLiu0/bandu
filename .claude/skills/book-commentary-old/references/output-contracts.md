# Six-stage output contracts

## Contents

- File sequence
- Common envelope
- Version 0.4 delivery fields
- Version 0.5 cognitive-reward fields
- Version 0.6 delivery-planning and style fields
- Version 0.7 dual-voice beat fields
- Unit conflicts
- Unit plans
- Unit comments
- Beat difficulties
- Beat plans
- Beat comments
- Referential integrity

## File sequence

Write exactly these stage files in the output directory:

```text
01-unit-conflicts.json
02-unit-plans.json
03-unit-comments.json
04-beat-difficulties.json
05-beat-plans.json
06-beat-comments.json
```

Never begin a stage before all prior numbered files validate.

## Common envelope

Every file must use:

```json
{
  "status": "ok",
  "schema_version": "0.7.0",
  "stage": "unit_conflicts",
  "source": {
    "document_id": "chapter1-prompt-chaining",
    "source_path": "content/bilingual/Chapter 1_ Prompt Chaining.md",
    "source_sha256": "..."
  },
  "settings": {
    "output_language": "zh-CN",
    "reader_profile": "curious beginner with no assumed domain knowledge",
    "unit_voice_policy": "select_one",
    "beat_voice_policy": "one_or_both",
    "voice_coverage_target": {
      "mentor": 0.7,
      "student": 0.7
    }
  },
  "items": [],
  "validation": {
    "errors": [],
    "warnings": []
  }
}
```

Use the exact stage names specified below. Keep `status: ok` only after completing the stage. The deterministic validator calculates counts; a hand-authored `stats` object is unnecessary in the MVP.

Use `schema_version: "0.7.0"` for all new runs. The validator continues to accept existing `0.1.0` through `0.6.0` artifacts as legacy output, but do not create new legacy artifacts. Legacy envelopes keep `settings.voice_policy: "select_one"`. Version `0.7.0` replaces that setting with separate unit and beat policies, retains a single selected voice for structural units, and allows one or both voices on every beat.

## Version 0.4 delivery fields

Use one `presentation_form` in every non-skipped unit plan and beat plan:

- `short_paragraph`
- `core_question`
- `arrow_chain`
- `bullet_breakdown`
- `contrast_pair`
- `mini_dialogue`
- `scene_then_point`

Copy the planned form into the corresponding third-stage output. The form describes the dominant visible shape, not every device used in the text.

Through schema `0.6.0`, keep reader-facing commentary in the existing JSON string fields and do not add parallel variants. In schema `0.7.0`, keep each beat voice's reader-facing commentary in its own `text` string inside `commentaries`; do not turn any individual `text` into an array. Represent intentional line breaks with escaped `\n`; bullets may use `- ` and process chains may use `→`.

Every non-skipped plan must also include:

```json
"analogy": {
  "use": true,
  "domain": "navigation",
  "mapping": "a real result changes the next planned step"
}
```

When no analogy is needed, use `{"use": false, "domain": null, "mapping": null}`. If `use` is true, `domain` and `mapping` must be non-empty. This object records a delivery decision, not permission to add external facts.

In third-stage `self_check`, set `analogy_mapped: true` only when the plan uses an analogy and the final text maps it cleanly back to the source. Set it to `null` when `use` is false.

## Version 0.5 cognitive-reward fields

Keep the six-file sequence. Through schema `0.6.0`, do not add parallel comment variants or change a final `text` string into an array. Schema `0.7.0` preserves one shared cognitive-reward brief per beat and stores one or two voice-specific plans and `text` strings around it.

Use these enums:

- `payoff.type`: `understanding`, `judgment`, `action`, `misconception_correction`, `connection`.
- `emotional_target`: `surprise`, `relief`, `control`, `curiosity`, `vigilance`.
- Entry function: `misconception`, `stakes`, `mystery`, `conflict`, `personal_relevance`.
- Explanation function: `analogy`, `personification`, `mini_scene`, `counterexample`, `contrast`, `missing_prerequisite`, `author_intent`, `source_trace`.
- Exit function: `payoff`, `mental_model`, `chapter_position`, `bridge`, `memory_anchor`.
- `loop_contract.action`: `close`, `close_and_open`.

For every non-skipped beat plan, include the following fields. This example assumes target `c01-s01-b06`, whose immediate next sibling is `c01-s01-b07`:

```json
"commentary_brief": {
  "reader_old_belief": "Using the same model makes the roles of individual steps interchangeable.",
  "central_question": "Why assign different roles when the underlying model is the same?",
  "tension": "The steps share a model but still need different task and output boundaries.",
  "information_turn": "A role constrains what one step should attend to and produce.",
  "payoff": {
    "type": "judgment",
    "statement": "The reader can distinguish model identity from step responsibility."
  },
  "emotional_target": "control",
  "next_dependency": {
    "target_id": "c01-s01-b07",
    "relationship": "the next beat shows how separately defined roles hand off results through structured output",
    "reader_need": "the reader needs to know how separate roles exchange a usable result",
    "why_current_stops": "the current beat defines role responsibility but not the structured handoff",
    "bridge_question": "If the roles are clear, what keeps their handoff from becoming vague?",
    "evidence_refs": [
      {"node_id": "c01-s01-b07", "field": "summary"}
    ]
  },
  "function_tags": {
    "entry": "misconception",
    "explanation": "contrast",
    "exit": "bridge"
  },
  "forbidden_exaggeration": [
    "Do not claim that assigning a role changes the underlying model."
  ]
},
"loop_contract": {
  "action": "close_and_open",
  "next_question": "If the roles are clear, what keeps their handoff from becoming vague?",
  "close_by_target_id": "c01-s01-b07",
  "close_by_evidence_refs": [
    {"node_id": "c01-s01-b07", "field": "summary"}
  ]
}
```

`reader_old_belief`, `central_question`, `tension`, `information_turn`, `payoff.statement`, and `forbidden_exaggeration` must be grounded in the current beat or recorded containing context. Always provide one payoff and one exit function. Entry and explanation functions may be `null` when unnecessary.

Set `next_dependency` to `null` when no direct dependency exists. When it is non-null, its `target_id` must be the immediate next sibling beat and every evidence reference must use that beat's `title`, `summary`, or `function`. Do not cite future `source_markdown`.

Use `loop_contract.action: "close"` with `next_question: null`, `close_by_target_id: null`, and `close_by_evidence_refs: []` when no loop is opened. Use `close_and_open` only with a non-null `next_dependency`; copy its `bridge_question` into `next_question`, choose the immediate or second next sibling as `close_by_target_id`, and cite that checkpoint's `title`, `summary`, or `function` in a non-empty `close_by_evidence_refs`. A beat-level loop must not cross its direct `beats[]` array.

## Version 0.6 delivery-planning and style fields

For every schema `0.6.0` beat plan, add `delivery_design` after `commentary_brief`:

```json
"delivery_design": {
  "human_anchor": "A writer hands a trend summary to the email-writing step, which needs named trends and supporting data rather than a vague paragraph.",
  "reader_reaction": "So the next step cannot just be told that the answer is somewhere in there?",
  "lively_turn": {
    "device": "role_dialogue",
    "source_relationship": "structured fields make the handoff explicit but do not guarantee factual correctness",
    "planned_move": "let the receiving step ask where the trend name and supporting data are"
  }
}
```

`human_anchor` must name a source-grounded person, role, object, action, result, or reading predicament that makes the relationship observable. `reader_reaction` must be a plausible short response from a curious beginner at this beat; it is planning material and need not appear verbatim in the final comment.

Allowed `lively_turn.device` values are `micro_scene`, `inner_monologue`, `role_dialogue`, `consequence_zoom`, `plainspoken_reframe`, and `none`. For every non-`none` device, provide non-empty `source_relationship` and `planned_move`. For `none`, set both fields to `null`. The lively turn is a delivery aid, not a second payoff, external story, or permission to distort the source.

In every non-skipped schema `0.6.0` or later unit comment, require `companion_voice: true` and `lecture_scaffolding_removed: true`. In every schema `0.6.0` or later beat commentary, require those two checks plus `human_entry_realized: true`. These checks confirm that the finished prose sounds like a reading companion, hides unnecessary planning structure, and realizes the beat's delivery design.

Also require a non-empty `form_rationale` in every non-skipped unit plan and every beat plan. State which source relationship the selected form makes easier to see. For a non-null schema `0.6.0` or later `next_dependency`, also require:

```json
"reader_need": "After seeing that roles differ, the reader needs to know how one role hands a usable result to the next.",
"why_current_stops": "The current beat defines role boundaries but does not explain the output contract used for handoff."
```

These fields distinguish a real knowledge dependency from mere topic continuity. Do not open a loop only because another related beat follows.

## Version 0.7 dual-voice beat fields

Schema `0.7.0` keeps stages 1 through 4 and all structural-unit payloads semantically unchanged. The common envelope uses `unit_voice_policy`, `beat_voice_policy`, and `voice_coverage_target` as defined above. Only the beat-plan and beat-comment item shapes change.

Every beat plan must contain a `comment_plans` array with one or two entries. Allowed voice sets are `mentor`, `student`, or canonical paired order `mentor` then `student`. A voice may appear only once. Every planned voice produces exactly one final commentary.

Keep `commentary_brief` and `loop_contract` once at the shared beat-plan level. Move voice-specific `delivery_design`, strategy, presentation form, analogy, tone, constraints, and type into `comment_plans`. When both voices are planned, require:

```json
"pairing_design": {
  "mentor_job": "Explain why named JSON fields make a handoff inspectable without verifying the truth of the contents.",
  "student_job": "Roast the false confidence created by tidy field labels.",
  "non_overlap": "The student must not reteach field validation; the mentor must not repeat the student's dressed-up-container punchline."
}
```

Use `pairing_design: null` for a single-voice beat. A paired design must contain all three non-empty fields. It must assign a reasoning bridge or explicit explanation to mentor and a source-grounded roast or plain-language verdict to student.

Every chapter must satisfy all of these coverage invariants in both stage 5 and stage 6:

- every beat has at least one planned and emitted voice;
- `mentor` covers at least `ceil(beat_count * voice_coverage_target.mentor)` beats;
- `student` covers at least `ceil(beat_count * voice_coverage_target.student)` beats;
- paired beats count once toward each voice's coverage.

These are chapter-level acceptance gates. Do not duplicate a voice within one beat or count the number of comments instead of the number of covered beats.

## 1. Unit conflicts

Use `stage: "unit_conflicts"`. Record every book/chapter/section/subsection exactly once:

```json
{
  "target_id": "c01-s01",
  "unit_type": "section",
  "parent_id": "c01",
  "title": "Prompt Chaining Pattern Overview / 提示词链模式概述",
  "eligibility": "generate",
  "context_quality": "complete",
  "missing_fields": [],
  "context_used": {
    "previous_id": null,
    "next_id": "c01-s02",
    "child_ids": ["c01-s01-b01", "c01-s01-b02"]
  },
  "conflict": {
    "type": "simplicity_vs_reliability",
    "reader_assumption": "...",
    "counterforce": "...",
    "stakes": "...",
    "open_loop": "...",
    "statement": "...",
    "evidence_refs": [
      {"node_id": "c01-s01", "field": "summary"}
    ],
    "confidence": "high"
  },
  "skip_reason": null
}
```

Allowed eligibility values: `generate`, `provisional`, `skip`. For `skip`, set `conflict` to `null` and provide `skip_reason`. For `provisional`, set `context_quality: "partial"` and list missing fields.

## 2. Unit plans

Use `stage: "unit_plans"`. Preserve eligibility from stage 1:

```json
{
  "target_id": "c01-s01",
  "unit_type": "section",
  "eligibility": "generate",
  "upstream": {"stage": "unit_conflicts", "target_id": "c01-s01"},
  "plan": {
    "primary_goal": "surface_misconception",
    "reader_before": "...",
    "reader_after": "...",
    "opening_angle": "counterintuitive contrast",
    "closing_angle": "diagnose a failure",
    "voice": "mentor",
    "presentation_form": "contrast_pair",
    "form_rationale": "the contrast exposes the difference between one overloaded prompt and linked focused steps",
    "analogy": {"use": false, "domain": null, "mapping": null},
    "reward_design": {
      "hook_function": "conflict",
      "promised_payoff": "The reader can explain why a smaller linked task is easier to control than one overloaded prompt.",
      "payoff_checkpoint_id": "c01-s01-b01",
      "emotional_target": "curiosity",
      "closing_function": "mental_model"
    },
    "tone_tags": ["clear", "curious", "light"],
    "constraints": {
      "must": ["..."],
      "avoid": ["..."],
      "spoiler_boundary": "Do not explain the chaining mechanism in the opening.",
      "opening_max_chars": 90,
      "question_max_chars": 60
    }
  },
  "skip_reason": null
}
```

For skipped targets, set `plan` to `null` and preserve the skip reason.

In schema `0.4.0` and later, every non-skipped plan must include `presentation_form` and `analogy`. Use the planned form for the opening hook; the closing question remains a separate spoken-language question.

In schema `0.5.0` and later, also include `reward_design`. `hook_function` must use an entry-function enum, `emotional_target` must use the shared enum, and `closing_function` must use an exit-function enum. `payoff_checkpoint_id` must identify one of the first two eligible direct children in source order. The promised payoff must be supported by that child and the current unit's conflict; it is a planning promise, not text to paste into the opening.

In schema `0.6.0` and later, also include a non-empty `form_rationale` explaining why the chosen opening form fits the source conflict.

## 3. Unit comments

Use `stage: "unit_comments"`:

```json
{
  "target_id": "c01-s01",
  "unit_type": "section",
  "eligibility": "generate",
  "upstream": {
    "conflict_target_id": "c01-s01",
    "plan_target_id": "c01-s01"
  },
  "commentary": {
    "opening_hook": {
      "voice": "mentor",
      "presentation_form": "contrast_pair",
      "text": "..."
    },
    "closing_question": {
      "voice": "mentor",
      "text": "...",
      "answerability": "within_unit"
    }
  },
  "reward_delivery": {
    "hook_function": "conflict",
    "payoff_checkpoint_id": "c01-s01-b01",
    "emotional_target": "curiosity",
    "closing_function": "mental_model"
  },
  "self_check": {
    "grounded": true,
    "analysis_aligned": true,
    "beginner_clear": true,
    "engaging": true,
    "narrative_momentum": true,
    "purpose_fulfilled": true,
    "voice_consistent": true,
    "non_redundant": true,
    "spoiler_safe": true,
    "length_ok": true,
    "readable_rhythm": true,
    "format_fit": true,
    "colloquial_and_concrete": true,
    "analogy_mapped": null,
    "hook_promise_specific": true,
    "payoff_checkpoint_grounded": true,
    "healthy_continuation": true,
    "companion_voice": true,
    "lecture_scaffolding_removed": true
  },
  "skip_reason": null
}
```

Allowed answerability values: `within_unit`, `reflection`, `forward_bridge`. For skipped targets, set `commentary` and `self_check` to `null`.

In schema `0.4.0` and later, `opening_hook.presentation_form` must match stage 2. Run all four readability checks from `commentary-guidelines.md` before setting the readability self-check fields. The closing question remains a spoken-language question and does not need a separate presentation form.

In schema `0.5.0` and later, copy the four corresponding stage-2 `reward_design` values into `reward_delivery`. Require `hook_promise_specific`, `payoff_checkpoint_grounded`, and `healthy_continuation` to be true. These fields mean that the opening names a precise knowledge question, the early child can actually begin paying it off, and continuation is motivated by a real source dependency rather than withheld explanation.

In schema `0.6.0` and later, also require `companion_voice` and `lecture_scaffolding_removed` to be true after running the corresponding third-stage prose tests.

## 4. Beat difficulties

Use `stage: "beat_difficulties"`. Record every beat exactly once:

```json
{
  "target_id": "c01-s01-b07",
  "unit_type": "beat",
  "parent_id": "c01-s01",
  "context_used": {
    "previous_id": "c01-s01-b06",
    "next_id": null,
    "second_next_id": null,
    "section_id": "c01-s01",
    "subsection_id": null,
    "chapter_id": "c01"
  },
  "difficulty": {
    "dimensions": {
      "abstraction": 1,
      "prerequisite_load": 1,
      "reasoning_gap": 1,
      "terminology_density": 1,
      "representation_complexity": 2
    },
    "score": 6,
    "level": "medium",
    "rationale": "...",
    "interest_seed": "Why an intermediate JSON object acts like a contract between steps."
  }
}
```

All dimension values must be integers from 0 to 2. `score` must equal their sum. Use `simple` for 0-3, `medium` for 4-6, and `hard` for 7-10. Always provide a non-empty `rationale` that explains the classification and records the reader friction evidenced by the beat, plus a non-empty `interest_seed`.

In schema `0.5.0` and later, include `second_next_id` in `context_used`; use `null` when absent. `next_id` and `second_next_id` must be the first and second following siblings in the same direct `beats[]` array. These IDs expose the allowed short-loop horizon; they do not authorize reading future `source_markdown`.

## 5. Beat plans

Use `stage: "beat_plans"`. Schemas `0.1.0` through `0.6.0` use the legacy single-voice item shape:

```json
{
  "target_id": "c01-s01-b07",
  "unit_type": "beat",
  "upstream": {"stage": "beat_difficulties", "target_id": "c01-s01-b07"},
  "difficulty_level": "medium",
  "plan": {
    "mode": "fun_explanation",
    "primary_goal": "make structured handoff intuitive",
    "angle": "misconception_correction",
    "voice": "mentor",
    "comment_type": "fun_commentary",
    "presentation_form": "core_question",
    "form_rationale": "the beat turns on one hidden guarantee, so a concrete question organizes the distinction",
    "analogy": {
      "use": false,
      "domain": null,
      "mapping": null
    },
    "commentary_brief": {
      "reader_old_belief": "A structured JSON output guarantees that the model answer is correct.",
      "central_question": "What does the JSON handoff actually guarantee?",
      "tension": "Named fields make a handoff inspectable but cannot verify the truth of their contents.",
      "information_turn": "Structure defines where each result goes and makes missing fields visible.",
      "payoff": {
        "type": "misconception_correction",
        "statement": "The reader can distinguish an inspectable handoff from a correctness guarantee."
      },
      "emotional_target": "control",
      "next_dependency": null,
      "function_tags": {
        "entry": "misconception",
        "explanation": "contrast",
        "exit": "mental_model"
      },
      "forbidden_exaggeration": [
        "Do not claim that JSON structure guarantees factual correctness."
      ]
    },
    "delivery_design": {
      "human_anchor": "A receiving step gets a JSON handoff with named fields but still needs the field contents to be true.",
      "reader_reaction": "The boxes are labeled, but who checked what was put inside them?",
      "lively_turn": {
        "device": "plainspoken_reframe",
        "source_relationship": "structure makes the handoff inspectable without guaranteeing correctness",
        "planned_move": "contrast a labeled handoff with verified contents"
      }
    },
    "loop_contract": {
      "action": "close",
      "next_question": null,
      "close_by_target_id": null,
      "close_by_evidence_refs": []
    },
    "tone_tags": ["plainspoken", "light"],
    "constraints": {
      "must": ["distinguish an inspectable handoff from a correctness guarantee"],
      "avoid": ["claiming JSON guarantees correctness"],
      "max_chars": 150
    }
  }
}
```

Schema `0.7.0` uses this one-or-both voice shape:

```json
{
  "target_id": "c01-s01-b07",
  "unit_type": "beat",
  "upstream": {"stage": "beat_difficulties", "target_id": "c01-s01-b07"},
  "difficulty_level": "medium",
  "plan": {
    "mode": "fun_explanation",
    "primary_goal": "make structured handoff intuitive",
    "angle": "misconception_correction",
    "commentary_brief": {
      "reader_old_belief": "A structured JSON output guarantees that the model answer is correct.",
      "central_question": "What does the JSON handoff actually guarantee?",
      "tension": "Named fields make a handoff inspectable but cannot verify the truth of their contents.",
      "information_turn": "Structure defines where each result goes and makes missing fields visible.",
      "payoff": {
        "type": "misconception_correction",
        "statement": "The reader can distinguish an inspectable handoff from a correctness guarantee."
      },
      "emotional_target": "control",
      "next_dependency": null,
      "function_tags": {
        "entry": "misconception",
        "explanation": "contrast",
        "exit": "mental_model"
      },
      "forbidden_exaggeration": [
        "Do not claim that JSON structure guarantees factual correctness."
      ]
    },
    "loop_contract": {
      "action": "close",
      "next_question": null,
      "close_by_target_id": null,
      "close_by_evidence_refs": []
    },
    "pairing_design": {
      "mentor_job": "Explain the difference between visible fields and verified contents.",
      "student_job": "Roast the false confidence produced by tidy field labels.",
      "non_overlap": "The student does not reteach validation; the mentor does not reuse the student's labeled-box punchline."
    },
    "comment_plans": [
      {
        "voice": "mentor",
        "comment_type": "fun_commentary",
        "contribution": "make the missing guarantee explicit",
        "strategy": "misconception_correction",
        "roast_move": null,
        "presentation_form": "core_question",
        "form_rationale": "one concrete question exposes the hidden difference between structure and truth",
        "analogy": {"use": false, "domain": null, "mapping": null},
        "delivery_design": {
          "human_anchor": "A receiving step sees all required JSON fields but still needs their contents to be true.",
          "reader_reaction": "The fields are present; what has actually been verified?",
          "lively_turn": {
            "device": "plainspoken_reframe",
            "source_relationship": "structure exposes missing fields without proving factual correctness",
            "planned_move": "separate a visible slot from a verified value"
          }
        },
        "tone_tags": ["plainspoken", "clear"],
        "constraints": {
          "must": ["distinguish an inspectable handoff from a correctness guarantee"],
          "avoid": ["claiming JSON guarantees correctness"],
          "max_chars": 150
        }
      },
      {
        "voice": "student",
        "comment_type": "roast",
        "contribution": "make tidy formatting feel insufficient rather than trustworthy",
        "strategy": "plain_language_reframe",
        "roast_move": "deadpan_relabeling",
        "presentation_form": "short_paragraph",
        "form_rationale": "a short verdict lets the false confidence and correction land in one beat",
        "analogy": {
          "use": true,
          "domain": "labeled packaging",
          "mapping": "labels identify where contents belong but do not prove the contents are correct"
        },
        "delivery_design": {
          "human_anchor": "A JSON object arrives with every field neatly labeled and unverified values inside.",
          "reader_reaction": "The package is labeled beautifully; the contents are still on their own.",
          "lively_turn": {
            "device": "consequence_zoom",
            "source_relationship": "clean structure can create confidence beyond what it guarantees",
            "planned_move": "praise the labels, then expose the unchecked contents"
          }
        },
        "tone_tags": ["plainspoken", "wry", "sharp_friend"],
        "constraints": {
          "must": ["roast confidence in formatting without denying its handoff value"],
          "avoid": ["first-person scaffolding", "reteaching the mentor explanation", "study questions"],
          "max_chars": 80
        }
      }
    ]
  }
}
```

Use `fun_brief` for simple beats and `fun_explanation` for medium/hard beats. For medium/hard beats, ground the explanation in the reader friction recorded in the upstream `rationale`; for simple beats, build from `interest_seed`.

In schemas `0.3.0` through `0.6.0`, set `comment_type` from the single selected voice and never request both types:

- `student` -> `roast`
- `mentor` -> `fun_commentary`

For schema `0.4.0` and later, include a positive `max_chars` chosen from the voice/difficulty guidance in `commentary-guidelines.md`. Do not include `min_chars`. Also include a valid `presentation_form` and `analogy` object for every selected delivery. For legacy schema `0.3.0`, retain positive `min_chars` and `max_chars` with `min_chars <= max_chars` so existing artifacts remain valid.

For schema `0.5.0` and later, also include `commentary_brief` and `loop_contract` exactly as defined in the version-level contract. Plan the brief and payoff before choosing voice, form, or analogy. A non-null `next_dependency` requires `loop_contract.action: "close_and_open"`; a null dependency requires `action: "close"`. Do not use voice or difficulty as a shortcut for payoff type.

For schema `0.6.0`, also include the single `delivery_design` exactly as defined above. Complete it after the cognitive brief and voice are stable and before choosing the final visible form.

Also require `form_rationale`. When `next_dependency` is non-null, require non-empty `reader_need` and `why_current_stops` inside it. The former states the unresolved reader need created by the current payoff; the latter states why the current beat cannot honestly close it. These are not reader-facing teaser lines.

For schema `0.7.0`:

- require one or two `comment_plans` entries with unique voices and canonical order `mentor`, then `student` when paired;
- keep `mode`, `primary_goal`, `angle`, `commentary_brief`, and `loop_contract` at the shared plan level;
- require every comment plan to contain `voice`, its locked `comment_type`, non-empty `contribution`, `strategy`, `roast_move`, `presentation_form`, `form_rationale`, `analogy`, `delivery_design`, non-empty `tone_tags`, and `constraints` with no `min_chars`;
- choose `strategy` from the matching `fun_brief` or `fun_explanation` strategy set in `commentary-guidelines.md`; the student-specific `roast_move` records how that cognitive strategy becomes a roast rather than a miniature lesson;
- use `roast_move: null` for mentor; for student choose one of `promise_vs_reality`, `literal_consequence`, `role_personification`, `everyday_mapping`, `deadpan_relabeling`, or `dialogue_snap`;
- require `pairing_design` exactly when two comment plans appear and require it to be null for a single-voice beat;
- require mentor whenever `loop_contract.action` is `close_and_open`; only that mentor plan may reserve space for or realize the bridge;
- keep student comments bridge-free and include no study question in their planned contribution or constraints;
- apply `form_rationale`, analogy, delivery-design, and maximum-length validation independently to every comment plan.

## 6. Beat comments

Use `stage: "beat_comments"`. Schemas `0.1.0` through `0.6.0` use the legacy single-voice item shape:

```json
{
  "target_id": "c01-s01-b07",
  "unit_type": "beat",
  "upstream": {
    "difficulty_target_id": "c01-s01-b07",
    "plan_target_id": "c01-s01-b07"
  },
  "difficulty_level": "medium",
  "mode": "fun_explanation",
  "comment_type": "fun_commentary",
  "presentation_form": "core_question",
  "commentary": {"voice": "mentor", "text": "..."},
  "reward_delivery": {
    "payoff_type": "misconception_correction",
    "emotional_target": "control",
    "function_tags": {
      "entry": "misconception",
      "explanation": "contrast",
      "exit": "mental_model"
    },
    "loop_action": "close",
    "next_dependency_target_id": null,
    "close_by_target_id": null
  },
  "self_check": {
    "grounded": true,
    "addresses_difficulty": true,
    "analysis_aligned": true,
    "beginner_clear": true,
    "engaging": true,
    "narrative_momentum": true,
    "voice_goal_fulfilled": true,
    "purpose_fulfilled": true,
    "voice_consistent": true,
    "non_redundant": true,
    "length_ok": true,
    "readable_rhythm": true,
    "format_fit": true,
    "colloquial_and_concrete": true,
    "analogy_mapped": null,
    "payoff_delivered": true,
    "competence_restored": true,
    "bridge_grounded": true,
    "no_fake_cliffhanger": true,
    "one_cognitive_job": true,
    "companion_voice": true,
    "lecture_scaffolding_removed": true,
    "human_entry_realized": true
  }
}
```

Schema `0.7.0` uses this one-or-both voice shape:

```json
{
  "target_id": "c01-s01-b07",
  "unit_type": "beat",
  "upstream": {
    "difficulty_target_id": "c01-s01-b07",
    "plan_target_id": "c01-s01-b07"
  },
  "difficulty_level": "medium",
  "mode": "fun_explanation",
  "commentaries": [
    {
      "voice": "mentor",
      "comment_type": "fun_commentary",
      "contribution": "make the missing guarantee explicit",
      "presentation_form": "core_question",
      "text": "字段都齐了，内容就一定是真的吗？不。字段只负责把交接位置标清，内容是否真实，还得另做验证。",
      "self_check": {
        "grounded": true,
        "addresses_difficulty": true,
        "analysis_aligned": true,
        "beginner_clear": true,
        "engaging": true,
        "narrative_momentum": true,
        "voice_goal_fulfilled": true,
        "purpose_fulfilled": true,
        "voice_consistent": true,
        "non_redundant": true,
        "length_ok": true,
        "readable_rhythm": true,
        "format_fit": true,
        "colloquial_and_concrete": true,
        "analogy_mapped": null,
        "payoff_delivered": true,
        "competence_restored": true,
        "bridge_grounded": true,
        "no_fake_cliffhanger": true,
        "one_cognitive_job": true,
        "companion_voice": true,
        "lecture_scaffolding_removed": true,
        "human_entry_realized": true,
        "student_roast_fulfilled": null,
        "first_person_not_crutch": null,
        "pair_complementary": true
      }
    },
    {
      "voice": "student",
      "comment_type": "roast",
      "contribution": "make tidy formatting feel insufficient rather than trustworthy",
      "presentation_form": "short_paragraph",
      "text": "箱子贴满标签，里面装错了照样能准时发货。JSON 管包装，不替内容验货。",
      "self_check": {
        "grounded": true,
        "addresses_difficulty": true,
        "analysis_aligned": true,
        "beginner_clear": true,
        "engaging": true,
        "narrative_momentum": true,
        "voice_goal_fulfilled": true,
        "purpose_fulfilled": true,
        "voice_consistent": true,
        "non_redundant": true,
        "length_ok": true,
        "readable_rhythm": true,
        "format_fit": true,
        "colloquial_and_concrete": true,
        "analogy_mapped": true,
        "payoff_delivered": true,
        "competence_restored": true,
        "bridge_grounded": true,
        "no_fake_cliffhanger": true,
        "one_cognitive_job": true,
        "companion_voice": true,
        "lecture_scaffolding_removed": true,
        "human_entry_realized": true,
        "student_roast_fulfilled": true,
        "first_person_not_crutch": true,
        "pair_complementary": true
      }
    }
  ],
  "reward_delivery": {
    "payoff_type": "misconception_correction",
    "emotional_target": "control",
    "function_tags": {
      "entry": "misconception",
      "explanation": "contrast",
      "exit": "mental_model"
    },
    "loop_action": "close",
    "next_dependency_target_id": null,
    "close_by_target_id": null
  },
  "pair_check": {
    "mentor_reward": "The reader understands what JSON structure does and does not guarantee.",
    "student_reward": "The reader remembers that tidy labels cannot inspect their own contents.",
    "non_redundant": true
  }
}
```

For `fun_brief`, use `addresses_difficulty: null`. For `fun_explanation`, use a boolean and accept only `true` in a completed artifact. In schema `0.2.0` and later, all four third-stage checks must be `true`; a draft that is accurate but abstract, generic, or disconnected from its plan is incomplete.

In schemas `0.3.0` through `0.6.0`, `comment_type` must match both stage 5 and the single commentary voice. In schema `0.7.0`, apply the same lock independently to every `commentaries` entry: `student` can emit only `roast`, and `mentor` can emit only `fun_commentary`. Set `voice_goal_fulfilled: true` only when a roast creates source-specific recognition and a knowing smile, or a fun commentary produces enjoyable understanding.

In schema `0.4.0` and later, every commentary's `presentation_form` must match its stage-5 plan and the text must realize that form. The commentary must not exceed its planned `max_chars`; there is no minimum. Require `readable_rhythm`, `format_fit`, and `colloquial_and_concrete` to be true. Set `analogy_mapped` according to the corresponding stage-5 analogy decision. For legacy schema `0.3.0`, continue enforcing the planned minimum and maximum.

In schema `0.5.0` and later, copy the planned payoff type, emotional target, function tags, loop action, next-dependency target, and closing checkpoint into `reward_delivery`. Require all five cognitive-reward self-checks to be true. `bridge_grounded: true` means either no bridge appears or the bridge follows the recorded immediate-next evidence and closes within the planned horizon. A student roast passes `payoff_delivered` only when its source-specific reaction itself carries the cognitive win; a generic complaint does not pass.

In schema `0.6.0` and later, also require `companion_voice`, `lecture_scaffolding_removed`, and `human_entry_realized` to be true. These checks must be based on the finished text, not inferred from the presence of `delivery_design` in stage 5.

For schema `0.7.0`:

- require `commentaries` to contain exactly one entry per stage-5 `comment_plans` entry, with identical voice order, locked type, contribution, and presentation form;
- copy the shared stage-5 payoff, emotional target, function tags, dependency target, loop action, and closing checkpoint once into item-level `reward_delivery`;
- validate length, form, analogy, delivery design, and all self-checks independently for each commentary;
- require `student_roast_fulfilled: true` and `first_person_not_crutch: true` for student, and require both fields to be null for mentor;
- require `pair_complementary: true` in both commentary self-checks when paired and null for a single-voice beat;
- require a non-null `pair_check` with non-empty `mentor_reward`, non-empty `student_reward`, and `non_redundant: true` exactly when both voices appear; use `pair_check: null` otherwise;
- forbid a question-mark bridge or copied `loop_contract.next_question` in student text; when the shared loop action is `close_and_open`, require mentor and realize the bridge only in mentor text;
- calculate chapter coverage from distinct beat IDs containing each voice, not from commentary count.

## Referential integrity

- Every stage must retain the same `target_id` set and source order as its corresponding source units.
- Stage 2 must agree with stage 1 eligibility.
- Stage 3 must agree with stage 2 voice, eligibility, presentation form, and analogy decision where the schema provides them.
- Stages 5 and 6 must agree with stage 4 difficulty.
- Through schema `0.6.0`, stage 6 must agree with stage 5 mode, voice, presentation form, and analogy decision where the schema provides them.
- In schema `0.7.0`, stage 6 must agree with stage 5 mode and contain exactly one commentary for every planned voice in the same canonical order. Each commentary must copy its plan's voice, locked type, contribution, and presentation form, and must follow its own analogy, delivery-design, and length decisions.
- In schema `0.5.0` and later, stage 3 must also copy stage 2 reward-delivery fields, and stage 6 must copy stage 5 payoff, emotional, function-tag, dependency, and loop fields.
- All six schema `0.7.0` files in one run must use identical `unit_voice_policy`, `beat_voice_policy`, and `voice_coverage_target` settings.
- In schema `0.7.0`, `pairing_design` and `pair_check` must both be null for a single-voice beat and both be populated for a paired beat. A paired beat must contain exactly mentor then student; duplicate voices are invalid.
- In every schema `0.7.0` chapter, the stage-5 and stage-6 voice coverage counts must independently meet both configured ceilings, and every beat must have at least one voice.
- A unit `payoff_checkpoint_id` must be one of its first two eligible direct children.
- A beat `next_dependency.target_id` must equal `context_used.next_id`; all future evidence references must use that target's `title`, `summary`, or `function`.
- A `close_and_open` loop must use a `close_by_target_id` equal to `context_used.next_id` or `context_used.second_next_id`, with non-empty evidence references to that target. A `close` loop must keep its next-question and checkpoint fields null and its checkpoint evidence list empty.
- In schema `0.7.0`, a `close_and_open` beat must include mentor, and the student text must not copy or independently realize `loop_contract.next_question`.
- The last beat in a direct `beats[]` array must use a null next dependency and a `close` loop.
- Do not change upstream artifacts to make a downstream draft validate; repair the earliest incorrect stage and rerun later stages.
