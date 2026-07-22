---
name: commentary-review
description: Quality-review a final book-commentary JSON against its original segmentation JSON across accuracy, consistency, simplicity, and fun. Use when auditing a <stem>.commentary.json without modifying it, grading commentary batches on a comparable 0-10 per-chapter scale, or producing one <base-stem>.review.json whose every finding carries verbatim evidence quotes from the commentary and the source markdown.
---

# Commentary Review

Audit one final commentary artifact against its original segmentation and write one structured review report. Never modify the commentary or segmentation files, and never read the pre-analysis file — judge the final reader-facing text against the source only.

## Required references

Read all three references before reviewing:

- Read [references/input-contract.md](references/input-contract.md) for the two inputs, the alignment gate, and per-pass read scope.
- Read [references/review-guidelines.md](references/review-guidelines.md) for dimension criteria, severity calibration, evidence rules, and score bands.
- Read [references/output-contract.md](references/output-contract.md) for the exact review.json shape.

## Input gate

Accept exactly two readable JSON files: the original segmentation (rooted at `book.chapters[]`, every beat with `source_markdown`) and the final commentary (`schema_version "0.7.0"`, `stage "book_commentary"`). Validate before reviewing:

```bash
python3 .claude/skills/commentary-review/scripts/validate_review.py <segmentation.json> <commentary.json>
```

Stop on validation errors. Do not repair, reorder, or reinterpret either input.

## Output location and invariants

Use an explicitly requested output path. Otherwise strip a trailing `.commentary` from the commentary stem and write `<base-stem>.review.json` beside it. For `chapter1-segmentation.commentary.json`, write `chapter1-segmentation.review.json`.

Write exactly one JSON document with `schema_version: "0.7.0"` and `stage: "commentary_review"`. Write findings and suggestions in Chinese (`zh-CN`) unless requested otherwise. Every finding's `commentary_quote` must be a verbatim substring of the referenced commentary text; every accuracy finding must carry at least one verbatim source quote.

## R0. Mechanical precheck

Run the advisory statistics script and keep its output:

```bash
python3 .claude/skills/commentary-review/scripts/precheck_review.py <segmentation.json> <commentary.json>
```

Treat its duplicate pairs, repeated openings, form runs, and term first-mentions as leads for R2 and R4, never as findings — every emitted finding still requires model-verified evidence from the texts themselves. Copy the stats object verbatim into the report's `precheck` field.

## R1. Accuracy pass (per item)

Walk commentary items in source order. For each beat text, read that beat's `source_markdown` (bilingual paragraphs are one semantic source) and hunt: fabricated facts, numbers, names, or capabilities; inverted or overstated claims; analogy details phrased as book claims; promises the source cannot support. For structural items, check the hook and question against the node's `title/summary/function/flow` and its direct children's summaries — dramatizing is allowed, asserting absent facts is not. Record candidate findings with verbatim quotes as you go.

## R2. Consistency sweep (whole chapter)

After R1 has visited every item, re-walk the chapter with three ledgers:

- form ledger: presentation form, opening pattern, device, roast target per text — flag runs of three or more identical forms and near-duplicate structures or jokes, seeded by precheck candidates;
- concept ledger: concept → first explaining item — flag later texts that re-explain instead of reuse;
- horizon ledger: reader position — flag texts explaining content whose source location is later than the current beat, verified by locating the later beat's `source_markdown`. Revealing a later payoff is a blocker; merely front-loading is major.

Reading later beats is allowed here; that is the reviewer's job, unlike the writer's.

## R3. Simplicity pass (per item)

Test each text: 一个零背景读者能否只靠这条评论跨过这个理解台阶？Flag unexplained first-use jargon, abstract-noun chains, sentences doing several jobs, explanations harder than their source passage, and analogies longer than the point they serve.

## R4. Fun pass (per item and chapter arc)

Flag hooks whose promise the unit cannot pay off, generic cliffhanger phrasing, quiz or teacherly tone, jokes needing background knowledge, closing questions with no pull, and stretches of five or more reward-free items (chapter-scope pattern finding). Respect the anti-noise rules: voice-contract sarcasm and taste preferences are not findings; fun findings are never blockers.

## R5. Score and write

Deduplicate candidates (one finding per occurrence; systemic repetition becomes one chapter-scope pattern finding). Sort findings by commentary item order and number them `F001…`. Score each chapter's four dimensions 0-10 within the severity caps, write one-sentence rationales, compute summary tallies and the verdict, then write the single document once and validate:

```bash
python3 .claude/skills/commentary-review/scripts/validate_review.py <segmentation.json> <commentary.json> --review <review.json>
```

Fix the report — never the inputs — until validation passes.

## Review discipline

- Copy every quote verbatim; keep each to the smallest proving span, at most 120 characters.
- Ground every finding in a reader cost; drop taste-only objections.
- Do not review against pre-analysis plans, and do not copy source prose, summaries, or ledgers into the report beyond evidence quotes.
- File a fact-true-but-overselling hook under fun; file a fact-false claim under accuracy.
- Never emit the ledgers; emit only the report.

## Execution model

Use one agent per chapter (up to ~100 beats) so all four dimensions share one memory and one set of ledgers. For multi-chapter books, run chapters in order, forward the concept ledger (concept → first-explaining chapter and item) so cross-chapter re-explanation stays catchable, then merge: combine findings, keep per-chapter scores, and compute `scores.global` as the items-weighted mean. (Multi-chapter merging is specified but unverified until a second chapter exists.)
