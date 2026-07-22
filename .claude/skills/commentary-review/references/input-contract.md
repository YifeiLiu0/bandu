# Review input contract

## Inputs

Accept exactly two readable UTF-8 JSON files:

1. the original segmentation JSON (ground truth), rooted at `book.chapters[]`;
2. the final commentary JSON (`schema_version "0.7.0"`, `stage "book_commentary"`).

Do not read `.pre-analysis.json` or any embedded conflict/difficulty/plan data. The review judges the final reader-facing text against the source only, independent of upstream plans.

## Segmentation shape

Require root `status: "ok"`, `document_id`, `source_path`, `source_sha256`, `book`.

- Book: `id`, `chapters`; `title` optional for a partial-book artifact.
- Chapter: `id`, `title`, `summary`, `function`, `flow`, `sections`.
- Section: `id`, `title`, `summary`, `function`, `flow`, `subsections`, `beats`.
- Subsection: `id`, `title`, `summary`, `function`, `flow`, `beats`.
- Beat: `id`, `title`, `summary`, `function`, `source_markdown`.

Treat bilingual source paragraphs as one semantic source.

## Commentary shape (the review surface)

Require envelope keys `status`, `schema_version`, `stage`, `source`, `settings`, `items`, `validation` with `status: "ok"` and empty `validation.errors`.

- Structural item: `target_id`, `unit_type` in `book|chapter|section|subsection`, `commentary` with `opening_hook {voice, presentation_form, text}` and `closing_question {voice, text, answerability}`.
- Beat item: `target_id`, `unit_type: "beat"`, `commentaries[]` each `{voice, comment_type, presentation_form, text}`.

## Alignment gate

Require before reviewing:

- commentary `source.source_sha256` equals segmentation root `source_sha256`;
- every commentary `target_id` exists in the segmentation with matching `unit_type`;
- every segmentation beat appears exactly once, in segmentation preorder;
- structural items form a subsequence of structural nodes in preorder (missing structural nodes are upstream-skipped units, not review targets).

Stop on any gate failure. Do not repair, reorder, or reinterpret either input.

## Read scope per pass

- Accuracy (R1): the current beat's `source_markdown`; for structural items, the node's `title/summary/function/flow` plus its direct children's `title/summary/function`.
- Consistency (R2): all commentary texts of the chapter in item order, plus later beats' `source_markdown`. Reading ahead is explicitly allowed for the reviewer — its job is spoiler detection, unlike the writer, who must not read future bodies.
- Simplicity (R3) and fun (R4): the commentary texts plus the same-node source needed to judge whether the text lowers the barrier truthfully.

Never read or cite pre-analysis fields, and never copy `source_markdown` or summaries into the report beyond evidence quotes.
