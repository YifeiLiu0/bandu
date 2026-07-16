# Single final-commentary output contract

## File and envelope

Write one `<base-stem>.commentary.json`:

```json
{
  "status": "ok",
  "schema_version": "0.7.0",
  "stage": "book_commentary",
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

Copy source metadata from the enriched input. Do not add other envelope or item fields.

## Item order

Flatten the enriched hierarchy in this preorder:

```text
book
  chapter
    section
      direct beats, in beats[] order
      subsection, in subsections[] order
        subsection beats, in beats[] order
```

Include a structural item only when its embedded `conflict` and structural `plan` are non-null. Include every beat. This produces the same reading order as the segmentation while omitting non-commentary source content.

## Structural item

Preserve the final A3 commentary shape:

```json
{
  "target_id": "c01-s01",
  "unit_type": "section",
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
  }
}
```

Allowed structural `unit_type`: `book`, `chapter`, `section`, `subsection`. Allowed `answerability`: `within_unit`, `reflection`, `forward_bridge`.

Both voices must match the embedded structural plan voice. `opening_hook.presentation_form` must match its planned form. Enforce the planned opening and question maximum lengths.

Do not emit an item for a skipped structural node. Do not emit eligibility, skip reason, upstream, reward delivery, self-check, conflict, or plan.

## Beat item

Preserve the reader-facing portion of the current B3 commentary shape:

```json
{
  "target_id": "c01-s01-b01",
  "unit_type": "beat",
  "commentaries": [
    {
      "voice": "mentor",
      "comment_type": "fun_commentary",
      "presentation_form": "scene_then_point",
      "text": "..."
    },
    {
      "voice": "student",
      "comment_type": "roast",
      "presentation_form": "short_paragraph",
      "text": "..."
    }
  ]
}
```

Emit exactly one entry for every embedded `comment_plans` entry, preserving order. Copy `voice`, locked `comment_type`, and `presentation_form`; add only the final `text`. Enforce each voice plan's `max_chars`.

Do not emit difficulty level, mode, reward delivery, contribution, self-check, pair check, difficulty, or plan.

## Excluded content

The final artifact must contain none of these keys at any depth:

```text
summary
function
flow
source_markdown
conflict
difficulty
plan
upstream
eligibility
skip_reason
reward_delivery
contribution
self_check
pair_check
```

The envelope's `source` metadata is allowed; source prose and analysis are not.

## Referential integrity

- Item IDs and order must exactly match eligible structural nodes and all beats in source preorder.
- Every structural item must agree with its embedded structural plan's voice, form, and length limits.
- Every beat item must agree with its embedded voice plans' count, order, locked types, forms, and length limits.
- Chapter voice coverage must reach the configured target for mentor and student.
