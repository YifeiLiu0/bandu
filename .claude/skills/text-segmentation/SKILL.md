---
name: text-segmentation
description: Segment Markdown books into hierarchical JSON from book to chapter to section to beat, using coarse beat boundaries, optional bilingual alignment, beat summaries and article-function labels, section/chapter/book rollups, arrow-style function flows, and a reproducible .mjs generation script for final artifacts.
---

# Text Segmentation

## 1. Scope

Use this skill to segment Markdown into:

```text
book
  └── chapter
      └── section
          └── subsection, optional
              └── beat
```

This is a general Markdown text segmentation skill.

A beat is not a paragraph. A beat is a meaningful teaching, narrative, argument, or reading unit. Prefer coarse beats.

Default beat rule:

```text
If a subsection is already concise, keep the whole subsection as one beat.
If a pseudo-subsection exists, use that pseudo-subsection as one beat.
Only split further when the subsection contains multiple distinct artifacts, clearly different content functions, or would otherwise exceed the beat size limits in Section 4.2. 

In terms of form：
1）A beat typically consists of about 2–3 paragraphs. 
2）If a paragraph is relatively long, it can be treated as a single beat; very long paragraphs may be split up, but in most cases, the integrity of the paragraph should be maintained. 
3）If one or more paragraphs are relatively short, multiple paragraphs can be combined into a single beat.
4）Bilingual paragraphs are counted as “idea pairs”; “artifact beats” may exceed 2–3 paragraphs.
```

## 2. Input Gate

Only process Markdown.

Accept input only when:

- `format` is `markdown` or `md`; or
- `source_path` ends with `.md` or `.markdown`; or
- the caller explicitly states that the raw text is Markdown.

For all other formats, return the unsupported JSON below and stop. Do not convert, summarize, segment, infer chapters, or call an LLM.

```json
{
  "status": "unsupported",
  "reason": "text-segmentation only supports Markdown input.",
  "detected_format": "unknown",
  "source_path": "",
  "operations_performed": [],
  "next_action": "terminate_without_segmentation"
}
```

`markdown` may be omitted only when the caller provides a readable Markdown file path and the runtime has file access.

## 3. Output Contract

Return only JSON. Do not wrap the output in Markdown code fences.

### 3.1 Required Hierarchy

Always output:

```text
book → chapters[] → sections[] → optional subsections[] → beats[]
```

Even a single chapter file must be wrapped in `book`. If no book title is available, use `null`; do not invent one.

### 3.2 ID Scheme

IDs must encode hierarchy:

```text
book:       book01
chapter:    c01
section:    c01-s01
subsection: c01-s01-ss01
beat:       c01-s01-b01
beat under subsection: c01-s01-ss01-b01
reference:  c01-ref01 or c01-s09-ref01
asset:      c01-asset01 or c01-s09-asset01
```

Do not use standalone beat IDs like `beat_001`.

### 3.3 Required Beat Metadata

Every beat must include:

- `summary`: a concise, content-specific summary.
- `function`: the beat's role in the article, not just its topic.

Use one summary language consistently unless bilingual summaries are requested.

Good summary:

```text
Explains why single prompts become unreliable for multifaceted tasks and introduces decomposition as the fix.
```

Bad summary:

```text
This beat discusses some content from the chapter.
```

### 3.4 Function Labels

Each beat must include a short snake_case `function` label.

Recommended labels:

- structure: `book_intro`, `chapter_intro`, `section_intro`, `conclusion`
- concept: `concept_overview`, `concept_definition`, `mechanism_explanation`, `comparison`
- problem / solution: `problem_statement`, `limitation`, `solution_explanation`
- example: `workflow_example`, `use_case`, `structured_output_example`
- implementation: `implementation_intro`, `setup_instruction`, `code_explanation`, `code_example`
- artifact: `table_explanation`, `visual_summary`, `references`, `asset_reference`

If none fits, use a clear new snake_case value. Do not use vague labels like `misc` unless unavoidable.

### 3.5 Non-Contiguous Bilingual Beats

When bilingual source and translation are separated by intervening material, a final beat may use non-contiguous `line_ranges`.

Use non-contiguous beats when all of these are true:

- the separated ranges express the same local idea in different languages,
- keeping the full contiguous span would make the beat too broad or mix distinct functions,
- the intervening material can stand as its own beat or belongs to another aligned beat,
- source order and full coverage remain clear.

For non-contiguous beats:

- `line_ranges` must list every included source span in original source order, such as `[[56, 58], [77, 79]]`,
- `start_line` must be the first included line and `end_line` must be the last included line,
- `source_markdown` must preserve the exact text from each included range and may join ranges with a single blank line,
- add `source_is_contiguous: false`,
- add `alignment_confidence`: `"high"`, `"medium"`, or `"low"`,
- add optional `text_en_lines` and `text_zh_lines` when they clarify the alignment.

Do not use a non-contiguous beat to hide unrelated text. Every non-empty non-heading source line must still be covered exactly once by some beat or reference block.

### 3.6 JSON Shape

Supported output shape:

The book-level `summary`, `function`, and `flow` fields shown below follow the rollup rules in Step 4.3. The `chapters` array below expands one representative chapter object; complete outputs must include every chapter in source order.

Final output must preserve the object field order shown in this JSON shape. In particular, place `summary`, `function`, and `flow` immediately after `title` at the book, chapter, and section levels when those fields are required; do not merely append them after `chapters`, `sections`, `subsections`, or `beats`.

```json
{
  "status": "ok",
  "document_id": "book_or_document_id",
  "source_path": "content/book/chapter-01.md",
  "format": "markdown",
  "language_mode": "monolingual_or_bilingual_or_mixed",
  "segmentation_strategy": "markdown_structure_coarse_beats",
  "stats": {
    "books": 1,
    "chapters": 2,
    "sections": 1,
    "subsections": 0,
    "beats": 1,
    "reference_blocks": 0
  },
  "book": {
    "id": "book01",
    "title": null,
    "summary": "Concise book-level summary synthesized from chapter summaries, functions, and flows.",
    "function": "conceptual_progression",
    "flow": "conceptual_foundation -> practice_application",
    "chapters": [
      {
        "id": "c01",
        "book_id": "book01",
        "title": "Chapter title",
        "summary": "Concise chapter-level summary synthesized from section summaries, functions, and flows.",
        "function": "conceptual_foundation",
        "flow": "conceptual_setup",
        "start_line": 1,
        "end_line": 100,
        "sections": [
          {
            "id": "c01-s01",
            "chapter_id": "c01",
            "title": "Section title",
            "summary": "Concise section-level summary synthesized from beat summaries and functions.",
            "function": "conceptual_setup",
            "flow": "concept_overview",
            "start_line": 1,
            "end_line": 50,
            "subsections": [],
            "beats": [
              {
                "id": "c01-s01-b01",
                "book_id": "book01",
                "chapter_id": "c01",
                "section_id": "c01-s01",
                "subsection_id": null,
                "title": "Beat title",
                "summary": "Concise content-specific summary.",
                "function": "concept_overview",
                "start_line": 1,
                "end_line": 10,
                "line_ranges": [[1, 10]],
                "source_markdown": "...",
                "contains_code": false,
                "contains_json": false,
                "contains_table": false,
                "contains_image": false,
                "contains_references": false
              }
            ]
          }
        ]
      }
    ]
  },
  "validation": {
    "coverage": "complete",
    "warnings": []
  }
}
```

Optional bilingual fields may be added where applicable: `title_en`, `title_zh`, `text_en`, `text_zh`, `text_en_lines`, `text_zh_lines`, `alignment_confidence`, `source_is_contiguous`.

Reference blocks should use hierarchical IDs such as `c01-ref01` or `c01-s09-ref01`, include `summary`, `function: "references"`, line ranges, `source_markdown`, and `contains_references: true`.

## 4. Segmentation Procedure

Run Steps 4.1-4.3 as gated stages. After each step, validate the result with the matching checklist in Section 5 and the repair loop in Section 5.5:

1. Step 4.1 -> validate with Section 5.1; continue to Step 4.2 only after it passes.
2. Step 4.2 -> validate with Section 5.2; continue to Step 4.3 only after it passes.
3. Step 4.3 -> validate with Section 5.3; finalize or return output only after it passes.

### 4.1 Step 1: Scripted Structural Segmentation

When file access is available, run the bundled deterministic parser first:

```bash
python3 .claude/skills/text-segmentation/scripts/segment_markdown.py path/to/source.md --output path/to/chapter1-segmentation.scripted.json --check
```

The script is responsible for the structural draft. It must segment Markdown in this order:

```text
book → chapter → section → optional subsection → pseudo-section → coarse beat
```

For each beat, the script must record structural data such as `id`, parent IDs, `start_line`, `end_line`, `line_ranges`, `source_markdown`, `boundary_reason`, artifact flags, and coverage metadata. The script may include heuristic `summary` and `function` placeholders, but these are not final semantic labels.

Save this scripted result as a separate artifact before any LLM refinement, using a clear name such as `chapter1-segmentation.scripted.json`.

The script must satisfy the Step 4.1 validation checklist in Section 5.1 before any LLM step.

If an existing output such as `chapter1-segmentation.scripted.json` is claimed to be the scripted structural result, verify that the script can regenerate the same structural segmentation. Compare structural fields such as IDs, hierarchy, line ranges, `source_markdown`, `boundary_reason`, and artifact flags. Ignore differences in final `summary` and `function` if they were produced later by the LLM refinement step.

If the script cannot regenerate the required structural draft, diagnose the cause first. If repair requires modifying the parser script, deterministic rules, or other hard requirements, explain the reason and proposed operations to the user and wait for approval before making those changes. Do not proceed to LLM beat refinement while structural coverage is incomplete or while artifact boundaries are unsafe.

### 4.2 Step 2: LLM Beat Refinement

After the script returns `status: "ok"`, load the scripted JSON and refine beats locally. Do not ask the LLM to rediscover chapters, sections, or the whole document structure.

Produce a refined draft from this step. Section 5 handles validation, finalization, and reporting.

For each scripted beat, ask the LLM to decide one of three actions:

1. `keep`: keep the beat boundary and generate final `summary` and `function`.
2. `split`: split the beat into smaller beats, then generate final `summary` and `function` for each new beat.
3. `merge`: merge this beat with one or more adjacent beats under the same parent, then generate final `summary` and `function` for the merged beat.

Use the main rule:

```text
In terms of content：
Each final beat should contain one primary teaching, narrative, argument, implementation, artifact, or reading function.

In terms of form：
1）A beat typically consists of about 2–3 paragraphs. 
2）If a paragraph is relatively long, it can be treated as a single beat; very long paragraphs may be split up, but in most cases, the integrity of the paragraph should be maintained. 
3）If one or more paragraphs are relatively short, multiple paragraphs can be combined into a single beat.
4）Bilingual paragraphs are counted as “idea pairs”; “artifact beats” may exceed 2–3 paragraphs.
```

Apply these bilingual alignment rules before deciding final beat boundaries:

- First identify bilingual correspondence at the idea level, not merely by adjacent paragraph order.
- Pair English and Chinese text that translates or restates the same local idea, even when an artifact, example, list, or code block appears between them.
- Do not leave a translation-only beat when its source-language counterpart exists under the same section or subsection.
- If a source paragraph introduces an artifact and the translation appears after the artifact, prefer one of these structures:
  - one contiguous reading beat containing the explanation, small illustrative artifact, caption, and paired translation when the artifact is directly supportive and the span remains concise,
  - one aligned explanation beat using non-contiguous `line_ranges`,
  - one standalone artifact beat,
  - one aligned post-artifact explanation beat if the after-text explains the artifact's consequence or use.
- If an artifact is inseparable from the explanation, or is merely a small illustrative figure with caption, keep it with the aligned bilingual beat; otherwise split it out as its own artifact beat.
- When uncertain whether two non-adjacent bilingual spans correspond, keep them together only with `alignment_confidence: "medium"` or `"low"` and add a validation warning.

Apply these beat size limits after bilingual alignment:

- A final beat should normally stay under about 1,200 English words, 1,800 Chinese characters, or 140 source lines, whichever comes first.
- A final beat that contains code, JSON, a table, or an image should normally contain only the setup needed to understand that artifact, the intact artifact, and any directly paired bilingual explanation.
- Split a beat that has more than one teachable artifact unless the artifacts are tiny and jointly serve one local function.
- Split a beat when it would require a long summary with multiple clauses joined by "and then", "also", or similar signals.
- Do not use the size limits to split source text away from its translation; use non-contiguous aligned beats instead.

Split a scripted beat when it is too long to explain comfortably or when it combines distinct functions. Typical split cases:

- A beat mixes setup explanation, installation command, code example, and post-code explanation, such as `c01-s03-b01`.
- A code block or table has a separate downstream role from the surrounding explanation.
- An image or figure should be split only when it carries an independent teaching function, is large enough to inspect on its own, or is reused as a reference asset beyond the local explanation.
- A pseudo-section contains multiple distinct artifacts or multiple stages that should be handled by different downstream subagents.
- A beat exceeds a comfortable reading or commentary size even though the script kept it as a coarse structural span.
- A bilingual pair is separated by an artifact and would otherwise force an oversized contiguous beat.

Merge adjacent scripted beats when they are too small to be meaningful alone and serve one local teaching function. Typical merge cases:

- Short adjacent pseudo-sections such as `What`, `Why`, and `Rule of thumb` inside an `At a Glance` section may be merged when the downstream experience benefits from reading them together.
- A beat and its adjacent translation-only or continuation beat should be merged if they express the same idea.
- Adjacent definition, small illustrative figure/caption, and translated caption should be merged when they form one reading moment and the combined beat remains concise.
- Several tiny beats should be merged when separate summaries/functions would be artificial.

Only merge contiguous beat spans that:

- are adjacent,
- belong to the same chapter, section, and subsection parent,
- preserve source order and full coverage,
- do not cross an unsafe artifact boundary,
- keep bilingual pairs together.

Non-contiguous bilingual alignment is not a merge. It is a refinement action that reassigns source line ranges within the same chapter, section, and subsection parent so corresponding source and translation stay together while intervening material remains separately covered.

When splitting or merging, update IDs, titles, line ranges, `source_markdown`, `boundary_reason`, artifact flags, parent IDs, stats, and validation metadata. Preserve original source text exactly; never paraphrase `source_markdown`.

Use the `summary` and `function` rules in Sections 3.3 and 3.4 to support boundary decisions.

Save this scripted result as a separate artifact before any LLM refinement, using a clear name such as `chapter1-segmentation.llm.json`.

The script must satisfy the Step 4.2 validation checklist in Section 5.2 before proceeding to step 3.

### 4.3 Step 3: Hierarchical Semantic Rollup

After final beat boundaries, beat summaries, and beat functions are stable, synthesize required section, chapter, and when applicable book rollups. Every section and every chapter must include `summary`, `function`, and `flow`. Do not use this step to change beat boundaries or to create array-style flow entries.

For each section:

- gather every descendant beat under the section, including beats nested inside subsections,
- preserve source order,
- use only each beat's `id`, `title`, `summary`, and `function` as the semantic source,
- generate section `summary` from the descendant beat summaries and functions,
- generate section `function` as the section's core role,
- generate section `flow` by joining the descendant beat `function` values in source order with ` -> `.

For each chapter:

- gather every section under the chapter,
- preserve source order,
- use only each section's `id`, `title`, `summary`, `function`, and `flow` as the semantic source,
- generate chapter `summary` from the child section summaries, functions, and flows,
- generate chapter `function` as the chapter's core role,
- generate chapter `flow` by joining the child section `function` values in source order with ` -> `.

For each multi-chapter book:

- gather every chapter under the book,
- preserve source order,
- use only each chapter's `id`, `title`, `summary`, `function`, and `flow` as the semantic source,
- generate book `summary` from the child chapter summaries, functions, and flows,
- generate book `function` as the book's core role,
- generate book `flow` by joining the child chapter `function` values in source order with ` -> `.

Rollup `summary` values must be concise, content-specific, and synthesized rather than simple concatenations of child summaries. Rollup `function` values must be short snake_case labels that name the parent unit's core role, not a copied child function. Prefer labels such as `conceptual_setup`, `problem_motivation`, `mechanism_development`, `implementation_walkthrough`, `example_application`, `practice_progression`, `synthesis`, or another clear article-function label. Rollup `flow` values must preserve source order, be built from child `function` values only, and remain plain strings such as `concept_definition -> mechanism_explanation -> problem_statement`; do not include IDs, titles, summaries, bullets, arrays, or objects inside `flow`.

Save this scripted result as a separate artifact before any LLM refinement, using a clear name such as `chapter1-segmentation.json`.

The script must satisfy the Step 4.3 validation checklist in Section 5.3 before writing the reproducibility script.

## 5. Validation and Finalization

Validate after the scripted pass, after LLM beat refinement, and again after hierarchical semantic rollup. Validation is a hard gate, not a suggestion. Do not proceed to the next step until the current validation gate passes. Do not return `status: "ok"` until validation passes.

### 5.1 Validate After Step 4.1

After document structure parsing, verify:

- input is confirmed as Markdown,
- parser protected boundaries for headings, code fences / code blocks, lists, blockquotes, tables, images / captions, link reference definitions, footnotes, and horizontal rules,
- chapters are mapped before sections, and sections are mapped before subsections,
- explicit chapter markers such as `Chapter 1`, `第 1 章`, or `第一章` are treated as chapter boundaries even when their Markdown level varies,
- if no explicit chapter exists, one inferred default chapter is created with ID `c01`,
- all chapters preserve the original order,
- all sections and subsections are attached to the correct parent chapter / section,
- bold lead labels are treated as pseudo-sections when a section has no heading-based subsections, such as `**Limitations of single prompts:**`, `**1. Information Processing Workflows:**`, `**What:**`, or `**问题背景：**`,
- no non-empty source content is missing,
- headings are represented as titles, not mistakenly included as body text,
- preface, introduction, appendix, notes, references, exercises, and similar non-standard parts are handled explicitly,
- inferred chapters / sections / subsections are clearly marked, such as `"inferred": true`,
- adjacent same-level bilingual headings are merged, source and translation stay together when they express the same local idea, and bilingual fields such as `title_en` / `title_zh` are added when useful,
- artifacts remain intact, with no split inside fenced code blocks, JSON examples, bash commands, Markdown tables, images and figure captions, link reference definitions, or footnotes,
- source spans are continuous where expected, or explicitly represented as non-contiguous bilingual refinement candidates,
- IDs encode hierarchy, such as `c01-s01-b01`.

### 5.2 Validate After Step 4.2

After beat parsing, verify:

- each beat expresses one main semantic action or reading unit,
- each beat is large enough to be meaningful,
- each beat is small enough to explain comfortably,
- each beat respects the beat size limits in Section 4.2 unless an explicit warning explains why a larger beat is necessary,
- If a beat contains four or more paragraphs (in the bilingual Chinese-English version, one pair counts as one paragraph), check whether there are any cases where the paragraphs cannot be split (e.g., extra paragraphs are direct setup, captions, or intact code/JSON/image/list content), or whether one or more of these paragraphs are relatively short; otherwise, the beat should be further split.
- If a beat contains only one paragraph or fewer, check whether that paragraph is relatively long; otherwise, it should be merged with another beat.
- each beat has a correct, content-specific `summary`,
- each beat has a clear `function`,
- each beat has a reasonable boundary reason, stored as `boundary_reason` when useful,
- all beats preserve original order and full source coverage,
- bilingual pairs stay together when applicable, including non-adjacent pairs separated by artifacts or examples,
- no translation-only beat remains when its source-language counterpart exists under the same parent,
- non-contiguous bilingual beats use multiple ordered `line_ranges`, `source_is_contiguous: false`, and `alignment_confidence`,
- every included range in a non-contiguous beat preserves exact source text and every intervening non-empty line is covered by another beat or reference block,
- artifacts are intact and not split internally,
- the reproducibility `.mjs` script exists, parses successfully with Node, and can regenerate the final artifacts,
- output is valid JSON only, with no Markdown code fence.

### 5.3 Validate After Step 4.3

After rollup generation, verify:

- every section has a content-specific `summary`,
- every section has a clear core `function`,
- every section has a non-empty `flow` unless the section has no beats,
- each section `flow` is exactly the section's descendant beat `function` values joined in source order with ` -> `,
- every chapter has a content-specific `summary`,
- every chapter has a clear core `function`,
- every chapter has a non-empty `flow` unless the chapter has no sections,
- each chapter `flow` is exactly the chapter's child section `function` values joined in source order with ` -> `,
- books with one chapter do not include book-level `summary`, `function`, or `flow`,
- books with more than one chapter have a content-specific `summary`,
- books with more than one chapter have a clear core `function`,
- books with more than one chapter have a non-empty `flow`,
- each book `flow` is exactly the book's child chapter `function` values joined in source order with ` -> `,
- final JSON object field order follows the layout in Section 3.6, especially for `summary`, `function`, and `flow` placement,
- rollup `summary` values are synthesized from child metadata rather than copied wholesale from `source_markdown`,
- rollup `function` values are short snake_case labels,
- rollup `flow` values are plain strings, not arrays or objects.

### 5.4 Statuses and Repair Loop

Use these statuses:

- `status: "unsupported"` when the input is not Markdown. Stop immediately and do not segment, summarize, infer structure, or call an LLM.
- `status: "invalid"` when Markdown input was processed but required output constraints still fail after repair attempts.
- `status: "ok"` only when all hard requirements pass.

If validation fails, repair the unreasonable parts before final output.

Typical repairs:

- reattach a section or subsection to the correct parent,
- restore missing source lines,
- move headings out of body text and into title fields,
- split an overlarge beat,
- merge beats that are too small or only differ by translation paragraph,
- re-align non-adjacent bilingual source and translation spans using non-contiguous `line_ranges`,
- split intervening artifacts out of oversized bilingual spans when they serve a distinct function,
- fix broken artifact boundaries,
- correct non-hierarchical IDs,
- add or correct missing `summary`, `function`, or `boundary_reason`,
- add or correct missing section/chapter/book `summary`, `function`, or `flow`,
- mark inferred structure explicitly.

After repair, run validation again. Repeat validation → repair until all hard requirements pass, or until no safe repair remains.

If no safe repair remains, return `status: "invalid"` with structured validation errors and warnings instead of returning a partial success.

Validation output should include enough detail to diagnose failures:

```json
{
  "validation": {
    "coverage": "complete_or_incomplete",
    "errors": [],
    "warnings": []
  }
}
```
### 5.5 Finalize and Report

After validation and any repair loop pass, also write a reproducibility script as a separate `.mjs` file, such as `scripts/segment-chapter1.mjs` or `scripts/build-chapter1-segmentation.mjs`. This script is a required artifact, not an optional convenience.

The `.mjs` script must:

- rebuild the scripted structural JSON from the Markdown source by invoking or faithfully reproducing the deterministic parser step,
- apply the final refinement decisions, including split / merge / non-contiguous bilingual alignment choices, semantic summaries, functions, reference IDs, and rollups,
- write the scripted JSON, final JSON, and difference report to the same paths used in the delivered artifacts unless explicit CLI flags override them,
- validate coverage, artifact integrity, required metadata, and rollup flows before writing `status: "ok"`,
- be runnable from the repository root with `node path/to/script.mjs`,
- avoid network access unless the source Markdown itself must be fetched and the user explicitly requested fetching,
- avoid hidden temporary notebooks, shell history, or one-off Python snippets as the only source of refinement logic.

When final semantic choices required human or LLM judgment, encode those choices in the `.mjs` script as structured refinement data or deterministic transformation rules so the final artifact can be regenerated from source.

After validation and any repair loop pass, also write a separate difference report, such as `chapter1-segmentation.diff.md`, that explains only the differences between the scripted result and the validated final result. Do not copy the full segmentation JSON or full `source_markdown` into this report.

The difference report must stay focused on change points. Include:

- scripted file path and validated final file path,
- reproducibility script path and exact command,
- stats before and after,
- kept beats count,
- split beats with old ID, old line range, new IDs, new line ranges, and reason,
- merged beats with old IDs, old line ranges, new ID, new line range, and reason,
- non-contiguous bilingual alignments with new ID, line ranges, alignment confidence, and reason,
- beats whose boundary stayed the same but whose `summary` or `function` changed,
- section, chapter, and book rollup `summary`, `function`, or `flow` fields added or materially changed,
- final validation status.

If there are no boundary changes, still write the report after validation and state that only metadata changed, or that no differences were found.
