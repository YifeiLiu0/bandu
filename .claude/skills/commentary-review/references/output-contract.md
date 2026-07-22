# Review output contract

## File and envelope

Write one `<base-stem>.review.json` (strip a trailing `.commentary` from the commentary stem). Exactly these envelope keys:

```json
{
  "status": "ok",
  "schema_version": "0.7.0",
  "stage": "commentary_review",
  "source": {
    "document_id": "chapter1-prompt-chaining",
    "source_path": "content/bilingual/Chapter 1_ Prompt Chaining.md",
    "source_sha256": "..."
  },
  "inputs": {
    "segmentation_path": "data/chapter1-segmentation.json",
    "commentary_path": "data/chapter1-segmentation.commentary.json",
    "commentary_sha256": "..."
  },
  "settings": {
    "output_language": "zh-CN",
    "reader_profile": "curious beginner with no assumed domain knowledge",
    "dimensions": ["accuracy", "consistency", "simplicity", "fun"],
    "severity_levels": ["blocker", "major", "minor"],
    "score_scale": "0-10"
  },
  "precheck": {},
  "findings": [],
  "scores": { "chapters": [], "global": {} },
  "summary": {},
  "validation": { "errors": [], "warnings": [] }
}
```

Copy `source` verbatim from the commentary envelope. `inputs.commentary_sha256` is the SHA-256 of the commentary file bytes. `precheck` is the verbatim stdout object of `precheck_review.py`. `settings` values are fixed as shown except `output_language`/`reader_profile`, which follow the run.

## Finding item

```json
{
  "finding_id": "F001",
  "target_id": "c01-s01-b01",
  "unit_type": "beat",
  "commentary_ref": { "kind": "beat_commentary", "index": 0, "voice": "mentor" },
  "related_target_ids": null,
  "dimension": "accuracy",
  "severity": "major",
  "issue": "评论把可选优化说成必须步骤，源文没有这个约束。",
  "evidence": {
    "commentary_quote": "…被引评论文本的字面子串…",
    "source_refs": [
      { "target_id": "c01-s01-b01", "quote_from": "source", "quote": "…原文字面子串…" }
    ]
  },
  "suggestion": "…一到两句可执行改法…"
}
```

Rules:

- All ten keys are always present. `finding_id` is sequential `F001`, `F002`, … in emission order.
- `dimension` ∈ `accuracy|consistency|simplicity|fun`. `severity` ∈ `blocker|major|minor`. `issue` and `suggestion` are non-empty Chinese text (per `output_language`).
- Occurrence finding: `commentary_ref` non-null with `kind` ∈ `opening_hook|closing_question|beat_commentary`; `index` and `voice` present only for `beat_commentary` and matching that entry in the commentary file; `related_target_ids` is null. `commentary_quote` is a verbatim substring of exactly the referenced text.
- Chapter-scope pattern finding: `unit_type: "chapter"`, `target_id` = the chapter id, `commentary_ref: null`, `related_target_ids` lists ≥2 involved item ids, and `commentary_quote` quotes one representative occurrence from those items' texts.
- `source_refs` entries have exactly `target_id`, `quote_from` ∈ `source|commentary`, `quote`. With `quote_from: "source"`, the quote is a verbatim substring of that beat's `source_markdown` (or, for a structural target, of its `title`/`summary`/`function`/`flow`). With `quote_from: "commentary"`, it is a verbatim substring of one of that item's commentary texts.
- Accuracy findings carry at least one `quote_from: "source"` reference. Quotes are ≤120 characters.
- Findings are sorted by the target item's position in commentary item order (pattern findings sort at their chapter item's position).

## Scores

```json
{
  "chapters": [
    {
      "chapter_id": "c01",
      "items_reviewed": 38,
      "dimensions": {
        "accuracy":    { "score": 8, "blockers": 0, "majors": 1, "minors": 2, "rationale": "…" },
        "consistency": { "score": 6, "blockers": 0, "majors": 2, "minors": 3, "rationale": "…" },
        "simplicity":  { "score": 9, "blockers": 0, "majors": 0, "minors": 1, "rationale": "…" },
        "fun":         { "score": 7, "blockers": 0, "majors": 1, "minors": 2, "rationale": "…" }
      }
    }
  ],
  "global": { "accuracy": 8.0, "consistency": 6.0, "simplicity": 9.0, "fun": 7.0 }
}
```

- One `chapters[]` entry per chapter present in the commentary items. `items_reviewed` counts the commentary items belonging to that chapter (its chapter item, its sections/subsections, its beats); the book item belongs to no chapter.
- Severity counts per dimension equal the tally of that chapter's findings (book-item findings count only in `summary`).
- `score` is an integer 0–10 honoring the caps/floor in review-guidelines. `rationale` is one sentence.
- `global` holds one number per dimension: the `items_reviewed`-weighted mean of chapter scores, rounded to one decimal.

## Summary

```json
{
  "verdict": "revise",
  "items_reviewed": 39,
  "items_with_findings": 11,
  "by_dimension": {
    "accuracy": { "blocker": 0, "major": 1, "minor": 2 },
    "consistency": { "blocker": 0, "major": 2, "minor": 3 },
    "simplicity": { "blocker": 0, "major": 0, "minor": 1 },
    "fun": { "blocker": 0, "major": 1, "minor": 2 }
  },
  "by_severity": { "blocker": 0, "major": 4, "minor": 8 },
  "top_issues": ["三到五条一句话中文摘要，按影响排序"]
}
```

- `items_reviewed` = total commentary items. `items_with_findings` = distinct `target_id` values among findings.
- `by_dimension` and `by_severity` equal the exact tallies over all findings.
- `top_issues`: 1–5 one-line Chinese summaries of the most impactful problems; empty only when there are no findings.
- `verdict` ∈ `pass|revise|rework`: `rework` iff any blocker exists; else `revise` iff any major; else `pass`.

## Excluded content

Never modify the segmentation or commentary files. Beyond evidence quotes, do not copy `source_markdown`, summaries, functions, flows, or any pre-analysis field into the report. Never emit the ledgers.
