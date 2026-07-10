# Chapter 1 Segmentation Diff

- Scripted structural file: `data/chapter1-segmentation.scripted.json`
- Validated final file: `data/chapter1-segmentation.json`
- LLM refinement draft: `data/chapter1-segmentation.llm.json`
- Reproducibility script: `scripts/build-chapter1-segmentation.mjs`
- Rebuild command: `node scripts/build-chapter1-segmentation.mjs`

## Stats

| Stage | Sections | Beats | Reference blocks |
| --- | ---: | ---: | ---: |
| Scripted | 9 | 21 | 1 |
| Final | 9 | 29 | 1 |

- Kept scripted beat ranges: 15
- Split scripted beats: 6
- Merged scripted beats: 0
- Non-contiguous bilingual alignments: 2
- Reference beat converted to reference block: 1

## Split Beats

- `c01-s01-b01` 9-27 -> `c01-s01-b01 9-15`, `c01-s01-b02 17-23`, `c01-s01-b03 25-27`. Separated definition/modularity, dependency/tool integration, and agentic foundation.
- `c01-s01-b03` 40-54 -> `c01-s01-b05 40-50`, `c01-s01-b06 52-54`. Separated the market-research chain example from the control and role-assignment explanation.
- `c01-s02-b03` 111-135 -> `c01-s02-b03 111-123`, `c01-s02-b04 125-135`. Separated query decomposition from the hybrid research-agent workflow.
- `c01-s02-b04` 137-159 -> `c01-s02-b05 137-151`, `c01-s02-b06 153-159`. Separated extraction validation loops from OCR normalization and calculator-tool delegation.
- `c01-s03-b01` 237-308 -> `c01-s03-b01 237-247`, `c01-s03-b02 249-255 + 306`, `c01-s03-b03 257-304 + 308`. Separated framework rationale, setup command/provider note, and the intact Python code artifact.
- `c01-s04-b01` 314-338 -> `c01-s04-b01 314-322`, `c01-s04-b02 324-330`, `c01-s04-b03 332-338`. Separated the figure definition, context-vs-prompt comparison, and optimization/system-maturity discussion.

## Non-contiguous Alignments

- `c01-s03-b02` aligns the English setup/install span `249-255` with the delayed Chinese provider note on line `306`.
- `c01-s03-b03` keeps the Python code fence intact on `257-304` and aligns it with the delayed Chinese code explanation on line `308`.

## Semantic Metadata

- Replaced heuristic scripted beat summaries/functions with content-specific summaries and article-function labels.
- Added section and chapter rollups. Section flows are generated from beat/reference functions in source order; the chapter flow is generated from section functions.
- Omitted book-level summary/function/flow because this artifact contains a single chapter.

