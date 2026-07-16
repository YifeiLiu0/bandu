# Embedded output contract

## Final shape and placement

The enriched file is the source segmentation JSON plus four node-local fields. Do not add a top-level schema envelope or provenance field.

```json
{
  "id": "c01-s01",
  "summary": "original",
  "function": "original",
  "flow": "original",
  "conflict": {"...": "A1 value"},
  "plan": {"...": "A2 value"},
  "subsections": [],
  "beats": []
}
```

```json
{
  "id": "c01-s01-b01",
  "summary": "original",
  "function": "original",
  "difficulty": {"...": "B1 value"},
  "plan": {"...": "B2 value"},
  "source_markdown": "original"
}
```

The embedded value is exactly the inner `conflict`, `difficulty`, or `plan` value from the former staged artifact. Do not embed `target_id`, `unit_type`, `parent_id`, `context_used`, `upstream`, `difficulty_level`, `eligibility`, or `skip_reason`; those were transport metadata. A null structural conflict implies a skipped non-expository target, and its structural plan must also be null.

## Temporary patch envelope

Use a temporary envelope only to apply one stage:

```json
{
  "schema_version": "1.0.0",
  "stage": "unit_conflicts",
  "items": [
    {"target_id": "c01-s01", "conflict": {}}
  ]
}
```

Allowed stages and item values:

| Step | `stage` | Targets | Inserted value |
|---|---|---|---|
| A1 / 1 | `unit_conflicts` | all structural nodes | `item.conflict` |
| A2 / 2 | `unit_plans` | all structural nodes | `item.plan` |
| B1 / 3 | `beat_difficulties` | all beats | `item.difficulty` |
| B2 / 4 | `beat_plans` | all beats | `item.plan` |

Patch items may retain former transport metadata for convenience; the apply script ignores it.

## A1 `conflict`

Use null for a non-expository target. Otherwise preserve this exact shape:

```json
{
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
}
```

## A2 structural `plan`

Use null exactly when `conflict` is null. Otherwise preserve:

```json
{
  "primary_goal": "surface_misconception",
  "reader_before": "...",
  "reader_after": "...",
  "opening_angle": "counterintuitive contrast",
  "closing_angle": "diagnose a failure",
  "voice": "mentor",
  "presentation_form": "contrast_pair",
  "form_rationale": "...",
  "analogy": {"use": false, "domain": null, "mapping": null},
  "reward_design": {
    "hook_function": "conflict",
    "promised_payoff": "...",
    "payoff_checkpoint_id": "c01-s01-b01",
    "emotional_target": "curiosity",
    "closing_function": "mental_model"
  },
  "tone_tags": ["clear", "curious", "light"],
  "constraints": {
    "must": ["..."],
    "avoid": ["..."],
    "spoiler_boundary": "...",
    "opening_max_chars": 90,
    "question_max_chars": 60
  }
}
```

## B1 `difficulty`

```json
{
  "dimensions": {
    "abstraction": 1,
    "prerequisite_load": 1,
    "reasoning_gap": 1,
    "terminology_density": 1,
    "representation_complexity": 0
  },
  "score": 4,
  "level": "medium",
  "rationale": "...",
  "difficulty_points": [
    {
      "label": "decomposition_handoff",
      "reader_friction": "...",
      "evidence": "..."
    }
  ],
  "interest_seed": "..."
}
```

## B2 beat `plan`

```json
{
  "mode": "fun_explanation",
  "primary_goal": "...",
  "target_difficulty_labels": ["decomposition_handoff"],
  "angle": "misconception_correction",
  "commentary_brief": {
    "reader_old_belief": "...",
    "central_question": "...",
    "tension": "...",
    "information_turn": "...",
    "payoff": {
      "type": "misconception_correction",
      "statement": "..."
    },
    "emotional_target": "control",
    "next_dependency": null,
    "function_tags": {
      "entry": "misconception",
      "explanation": "contrast",
      "exit": "mental_model"
    },
    "forbidden_exaggeration": ["..."]
  },
  "loop_contract": {
    "action": "close",
    "next_question": null,
    "close_by_target_id": null,
    "close_by_evidence_refs": []
  },
  "pairing_design": null,
  "comment_plans": [
    {
      "voice": "mentor",
      "comment_type": "fun_commentary",
      "contribution": "...",
      "strategy": "misconception_correction",
      "roast_move": null,
      "presentation_form": "core_question",
      "form_rationale": "...",
      "analogy": {"use": false, "domain": null, "mapping": null},
      "delivery_design": {
        "human_anchor": "...",
        "reader_reaction": "...",
        "lively_turn": {
          "device": "plainspoken_reframe",
          "source_relationship": "...",
          "planned_move": "..."
        }
      },
      "tone_tags": ["plainspoken", "clear"],
      "constraints": {
        "must": ["..."],
        "avoid": ["..."],
        "max_chars": 150
      }
    }
  ]
}
```

When both voices are present, use canonical order `mentor`, then `student`, and set `pairing_design` to `mentor_job`, `student_job`, and `non_overlap`. When one voice is present, set `pairing_design` to null. A non-null `next_dependency` adds `target_id`, `relationship`, `reader_need`, `why_current_stops`, `bridge_question`, and `evidence_refs`, and requires `loop_contract.action: close_and_open` with matching checkpoint evidence.
