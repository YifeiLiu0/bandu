import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const ROOT = process.cwd();
const SOURCE_REL = 'content/bilingual/Chapter 1_ Prompt Chaining.md';
const SOURCE_PATH = path.join(ROOT, SOURCE_REL);
const PARSER_REL = '.claude/skills/text-segmentation/scripts/segment_markdown.py';
const PARSER_PATH = path.join(ROOT, PARSER_REL);
const DATA_DIR = path.join(ROOT, 'data');
const SCRIPTED_REL = 'data/chapter1-segmentation.scripted.json';
const LLM_REL = 'data/chapter1-segmentation.llm.json';
const FINAL_REL = 'data/chapter1-segmentation.json';
const DIFF_REL = 'data/chapter1-segmentation.diff.md';
const SCRIPT_REL = 'scripts/build-chapter1-segmentation.mjs';
const SCRIPTED_PATH = path.join(ROOT, SCRIPTED_REL);
const LLM_PATH = path.join(ROOT, LLM_REL);
const FINAL_PATH = path.join(ROOT, FINAL_REL);
const DIFF_PATH = path.join(ROOT, DIFF_REL);

const SECTION_DEFS = [
  {
    id: 'c01-s01',
    title: 'Prompt Chaining Pattern Overview / 提示词链模式概述',
    start_line: 5,
    end_line: 82,
    summary:
      'Introduces prompt chaining as a divide-and-conquer pattern, explains why single prompts fail under complex requirements, and shows how sequential decomposition and structured outputs make chains more reliable.',
    function: 'conceptual_setup',
    beats: [
      {
        title: 'Definition and Modularity',
        ranges: [[9, 15]],
        summary:
          'Defines prompt chaining as a pipeline pattern that decomposes a complex task into smaller prompts and makes each step easier to understand, debug, and optimize.',
        function: 'concept_definition',
        boundary_reason: 'semantic_split_from_scripted_overview',
      },
      {
        title: 'Dependency Chain and Tool Integration',
        ranges: [[17, 23]],
        summary:
          'Explains that each step passes context forward and that chains can call external systems, APIs, or databases to extend model capability.',
        function: 'mechanism_explanation',
        boundary_reason: 'semantic_split_from_scripted_overview',
      },
      {
        title: 'Agentic Foundation',
        ranges: [[25, 27]],
        summary:
          'Frames prompt chaining as a foundation for agents that need multi-step reasoning, planning, decision-making, and action in dynamic environments.',
        function: 'agentic_foundation',
        boundary_reason: 'semantic_split_from_scripted_overview',
      },
      {
        title: 'Limitations of Single Prompts',
        ranges: [[29, 38]],
        summary:
          'Shows how one oversized prompt can lead to instruction neglect, context drift, amplified errors, context-window problems, and hallucination.',
        function: 'limitation',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Sequential Decomposition Workflow',
        ranges: [[40, 50]],
        summary:
          'Uses a market-research pipeline to show how summarization, trend extraction, and email drafting can be chained as focused steps.',
        function: 'workflow_example',
        boundary_reason: 'semantic_split_inside_reliability_subsection',
      },
      {
        title: 'Granular Control and Role Assignment',
        ranges: [[52, 54]],
        summary:
          'Explains that smaller steps reduce ambiguity and allow each stage to use a distinct role such as analyst or documentation writer.',
        function: 'control_explanation',
        boundary_reason: 'semantic_split_inside_reliability_subsection',
      },
      {
        title: 'Structured Output Between Steps',
        ranges: [[56, 81]],
        summary:
          'Explains why chain reliability depends on well-formed intermediate data and uses a JSON trend object as the transfer format between prompts.',
        function: 'structured_output_example',
        boundary_reason: 'kept_artifact_with_direct_bilingual_explanation',
      },
    ],
  },
  {
    id: 'c01-s02',
    title: 'Practical Applications & Use Cases / 实际应用与用例',
    start_line: 83,
    end_line: 232,
    summary:
      'Catalogs practical prompt-chaining applications across information processing, complex answering, extraction, content generation, conversational state, code refinement, and multimodal reasoning.',
    function: 'use_case_catalog',
    beats: [
      {
        title: 'Use Case Scope',
        ranges: [[87, 89]],
        summary:
          'Introduces prompt chaining as a general-purpose pattern for turning complex agentic problems into manageable sequential steps.',
        function: 'section_intro',
        boundary_reason: 'kept_scripted_section_intro',
      },
      {
        title: 'Information Processing Workflows',
        ranges: [[91, 109]],
        summary:
          'Presents a document-processing chain that extracts text, summarizes it, pulls entities, searches a knowledge base, and generates a report.',
        function: 'workflow_example',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Complex Query Decomposition',
        ranges: [[111, 123]],
        summary:
          'Breaks a multifaceted historical question into sub-question identification, targeted retrieval, and synthesis steps.',
        function: 'query_decomposition_example',
        boundary_reason: 'semantic_split_inside_complex_query_use_case',
      },
      {
        title: 'Hybrid Research Workflows',
        ranges: [[125, 135]],
        summary:
          'Explains how research agents can combine parallel extraction across sources with sequential collation, synthesis, review, and refinement.',
        function: 'hybrid_workflow_explanation',
        boundary_reason: 'semantic_split_inside_complex_query_use_case',
      },
      {
        title: 'Data Extraction Validation Loop',
        ranges: [[137, 151]],
        summary:
          'Describes iterative extraction from unstructured documents where validation triggers follow-up prompts for missing or malformed fields.',
        function: 'extraction_workflow_example',
        boundary_reason: 'semantic_split_inside_data_extraction_use_case',
      },
      {
        title: 'OCR Normalization and Tool Use',
        ranges: [[153, 159]],
        summary:
          'Uses OCR processing to show a chain that extracts text, normalizes values, delegates arithmetic to a calculator, and reintegrates the exact result.',
        function: 'tool_augmented_workflow_example',
        boundary_reason: 'semantic_split_inside_data_extraction_use_case',
      },
      {
        title: 'Content Generation Workflows',
        ranges: [[161, 181]],
        summary:
          'Shows content generation as a staged workflow of ideation, outline creation, section drafting, and final revision.',
        function: 'content_workflow_example',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Conversational Agents with State',
        ranges: [[183, 199]],
        summary:
          'Explains how prompt chains can preserve conversational continuity by extracting intent and entities, updating state, and using that state in later turns.',
        function: 'state_management_example',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Code Generation and Refinement',
        ranges: [[201, 219]],
        summary:
          'Frames code generation as a multi-stage chain that outlines, drafts, analyzes, refines, documents, tests, and inserts deterministic validation between model calls.',
        function: 'code_workflow_example',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Multimodal and Multi-step Reasoning',
        ranges: [[221, 231]],
        summary:
          'Applies prompt chaining to multimodal interpretation by extracting image text, linking labels, and using tabular context to infer the answer.',
        function: 'multimodal_workflow_example',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
    ],
  },
  {
    id: 'c01-s03',
    title: 'Hands-On Code Example / 实操代码示例',
    start_line: 233,
    end_line: 309,
    summary:
      'Moves from implementation choices to a concrete LangChain example, separating framework rationale, setup requirements, and the executable two-step chain.',
    function: 'implementation_walkthrough',
    beats: [
      {
        title: 'Framework Choice and Pipeline Goal',
        ranges: [[237, 247]],
        summary:
          'Explains that prompt chains can be implemented with direct calls or orchestration frameworks, then narrows the demo to a linear LangChain/LangGraph-style data pipeline.',
        function: 'implementation_intro',
        boundary_reason: 'split_large_code_section_before_setup_artifact',
      },
      {
        title: 'Install and Provider Setup',
        ranges: [
          [249, 255],
          [306, 306],
        ],
        summary:
          'Gives the package installation command and notes that the OpenAI package can be swapped for another provider with matching credentials.',
        function: 'setup_instruction',
        boundary_reason: 'non_contiguous_bilingual_alignment_around_code_artifact',
        source_is_contiguous: false,
        alignment_confidence: 'high',
        text_en_lines: [[249, 255]],
        text_zh_lines: [[306, 306]],
      },
      {
        title: 'Two-step LangChain Prompt Chain',
        ranges: [
          [257, 304],
          [308, 308],
        ],
        summary:
          'Demonstrates a Python chain that extracts laptop specifications with one prompt, passes them into a transformation prompt, and prints the final JSON-like output.',
        function: 'code_example',
        boundary_reason: 'non_contiguous_bilingual_alignment_keeps_code_with_explanation',
        source_is_contiguous: false,
        alignment_confidence: 'high',
        text_en_lines: [[257, 304]],
        text_zh_lines: [[308, 308]],
      },
    ],
  },
  {
    id: 'c01-s04',
    title: 'Context Engineering and Prompt Engineering / 上下文工程和提示工程',
    start_line: 310,
    end_line: 339,
    summary:
      'Contrasts prompt engineering with context engineering by defining the richer context environment, illustrating it visually, and explaining feedback-driven context improvement.',
    function: 'context_engineering_comparison',
    beats: [
      {
        title: 'Context Engineering Definition and Figure',
        ranges: [[314, 322]],
        summary:
          'Defines context engineering as building a complete informational environment for the model and anchors the idea with a figure and bilingual caption.',
        function: 'visual_concept_definition',
        boundary_reason: 'split_visual_artifact_with_caption_and_translation',
      },
      {
        title: 'Beyond Prompt Wording',
        ranges: [[324, 330]],
        summary:
          'Explains how context engineering expands beyond phrasing to include system prompts, retrieved documents, tool outputs, user identity, history, and environmental state.',
        function: 'comparison',
        boundary_reason: 'semantic_split_after_visual_definition',
      },
      {
        title: 'Context Optimization and System Maturity',
        ranges: [[332, 338]],
        summary:
          'Shows how automated prompt and context optimization can support feedback loops and turn stateless chatbots into situationally aware systems.',
        function: 'optimization_methodology',
        boundary_reason: 'semantic_split_for_feedback_loop_and_conclusion',
      },
    ],
  },
  {
    id: 'c01-s05',
    title: 'At a Glance / 速览',
    start_line: 340,
    end_line: 355,
    summary:
      'Compresses the chapter into a quick problem-solution-guideline reference for when and why to use prompt chaining.',
    function: 'quick_reference',
    beats: [
      {
        title: 'What',
        ranges: [[344, 346]],
        summary:
          'Recaps the core problem: complex tasks overload a single prompt and increase instruction loss, context drift, and inaccurate outputs.',
        function: 'problem_recap',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Why',
        ranges: [[348, 350]],
        summary:
          'Recaps prompt chaining as a standardized way to decompose work into focused steps that pass outputs forward and improve control.',
        function: 'solution_recap',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
      {
        title: 'Rule of Thumb',
        ranges: [[352, 354]],
        summary:
          'Gives the usage guideline: choose prompt chaining for tasks with multiple stages, external tool interaction, state, or multi-step reasoning.',
        function: 'usage_guideline',
        boundary_reason: 'kept_scripted_pseudo_subsection',
      },
    ],
  },
  {
    id: 'c01-s06',
    title: 'Visual summary / 可视化摘要',
    start_line: 356,
    end_line: 365,
    summary:
      'Provides a visual representation of chained agents where each output becomes the next agent input.',
    function: 'visual_summary',
    beats: [
      {
        title: 'Prompt Chaining Pattern Figure',
        ranges: [[360, 364]],
        summary:
          'Uses a diagram and bilingual caption to summarize prompt chaining as a sequence of agents passing outputs forward.',
        function: 'visual_summary',
        boundary_reason: 'kept_scripted_visual_artifact',
      },
    ],
  },
  {
    id: 'c01-s07',
    title: 'Key Takeaways / 关键要点',
    start_line: 366,
    end_line: 383,
    summary:
      'Summarizes the chapter into the core claims that prompt chaining decomposes work, passes outputs between steps, improves reliability, and is supported by orchestration frameworks.',
    function: 'summary',
    beats: [
      {
        title: 'Key Takeaways',
        ranges: [[370, 382]],
        summary:
          'Lists the main takeaways: prompt chaining is also called the Pipeline pattern, uses previous outputs as inputs, improves manageability, and can be implemented with frameworks.',
        function: 'key_takeaways',
        boundary_reason: 'kept_scripted_summary_list',
      },
    ],
  },
  {
    id: 'c01-s08',
    title: 'Conclusion / 结论',
    start_line: 384,
    end_line: 391,
    summary:
      'Concludes that prompt chaining is a foundational pattern for reliable, context-aware systems that go beyond single-prompt capabilities.',
    function: 'conclusion',
    beats: [
      {
        title: 'Conclusion',
        ranges: [[388, 390]],
        summary:
          'Reinforces prompt chaining as a divide-and-conquer framework that improves control and enables agents with reasoning, tools, and state.',
        function: 'conclusion',
        boundary_reason: 'kept_scripted_conclusion',
      },
    ],
  },
  {
    id: 'c01-s09',
    title: 'References / 参考文献',
    start_line: 392,
    end_line: 405,
    summary:
      'Collects documentation and guide references for LCEL, LangGraph, chaining prompts, prompting concepts, CrewAI, Google prompting, Vertex Prompt Optimizer, and image assets.',
    function: 'references',
    reference_blocks: [
      {
        id: 'c01-s09-ref01',
        title: 'References',
        ranges: [[396, 405]],
        summary:
          'Lists external references and local image reference definitions used by the chapter.',
        function: 'references',
        boundary_reason: 'converted_scripted_reference_beat_to_reference_block',
      },
    ],
  },
];

const CHANGE_LOG = [
  {
    oldId: 'c01-s01-b01',
    oldRange: '9-27',
    newRanges: ['c01-s01-b01 9-15', 'c01-s01-b02 17-23', 'c01-s01-b03 25-27'],
    reason: 'Separated definition/modularity, dependency/tool integration, and agentic foundation.',
  },
  {
    oldId: 'c01-s01-b03',
    oldRange: '40-54',
    newRanges: ['c01-s01-b05 40-50', 'c01-s01-b06 52-54'],
    reason: 'Separated the market-research chain example from the control and role-assignment explanation.',
  },
  {
    oldId: 'c01-s02-b03',
    oldRange: '111-135',
    newRanges: ['c01-s02-b03 111-123', 'c01-s02-b04 125-135'],
    reason: 'Separated query decomposition from the hybrid research-agent workflow.',
  },
  {
    oldId: 'c01-s02-b04',
    oldRange: '137-159',
    newRanges: ['c01-s02-b05 137-151', 'c01-s02-b06 153-159'],
    reason: 'Separated extraction validation loops from OCR normalization and calculator-tool delegation.',
  },
  {
    oldId: 'c01-s03-b01',
    oldRange: '237-308',
    newRanges: [
      'c01-s03-b01 237-247',
      'c01-s03-b02 249-255 + 306',
      'c01-s03-b03 257-304 + 308',
    ],
    reason: 'Separated framework rationale, setup command/provider note, and the intact Python code artifact.',
  },
  {
    oldId: 'c01-s04-b01',
    oldRange: '314-338',
    newRanges: ['c01-s04-b01 314-322', 'c01-s04-b02 324-330', 'c01-s04-b03 332-338'],
    reason: 'Separated the figure definition, context-vs-prompt comparison, and optimization/system-maturity discussion.',
  },
];

async function main() {
  await mkdir(DATA_DIR, { recursive: true });
  runScriptedParser();

  const sourceText = await readFile(SOURCE_PATH, 'utf8');
  const lines = splitLines(sourceText);
  const scripted = JSON.parse(await readFile(SCRIPTED_PATH, 'utf8'));
  if (scripted.status !== 'ok') {
    throw new Error(`${SCRIPTED_REL} is not valid: ${JSON.stringify(scripted.validation)}`);
  }

  const llmDraft = buildDocument({ lines, includeRollups: false });
  llmDraft.validation = validateDocument(llmDraft, lines, { requireRollups: false });
  llmDraft.status = llmDraft.validation.errors.length ? 'invalid' : 'ok';

  const finalDocument = buildDocument({ lines, includeRollups: true });
  finalDocument.validation = validateDocument(finalDocument, lines, { requireRollups: true });
  finalDocument.status = finalDocument.validation.errors.length ? 'invalid' : 'ok';

  if (llmDraft.status !== 'ok') {
    throw new Error(`LLM refinement validation failed:\n${llmDraft.validation.errors.join('\n')}`);
  }
  if (finalDocument.status !== 'ok') {
    throw new Error(`Final validation failed:\n${finalDocument.validation.errors.join('\n')}`);
  }

  await writeJson(LLM_PATH, llmDraft);
  await writeJson(FINAL_PATH, finalDocument);
  await writeFile(DIFF_PATH, buildDiffReport(scripted, finalDocument), 'utf8');

  console.log(`Wrote ${SCRIPTED_REL}`);
  console.log(`Wrote ${LLM_REL}`);
  console.log(`Wrote ${FINAL_REL}`);
  console.log(`Wrote ${DIFF_REL}`);
  console.log(
    `Stats: ${finalDocument.stats.sections} sections, ${finalDocument.stats.beats} beats, ${finalDocument.stats.reference_blocks} reference block`
  );
}

function runScriptedParser() {
  execFileSync(
    'python3',
    [PARSER_PATH, SOURCE_PATH, '--output', SCRIPTED_PATH, '--check'],
    { stdio: 'inherit' }
  );
}

function buildDocument({ lines, includeRollups }) {
  const sections = SECTION_DEFS.map((sectionDef) => buildSection(sectionDef, lines, includeRollups));
  const chapterFlow = sections.map((section) => section.function).filter(Boolean).join(' -> ');
  const chapterBase = {
    id: 'c01',
    book_id: 'book01',
    title: 'Chapter 1: Prompt Chaining / 第 1 章：提示词链',
  };
  const chapter = includeRollups
    ? {
        ...chapterBase,
        summary:
          'Explains prompt chaining from concept and motivation through practical workflows, implementation, context engineering, quick reference material, visual summaries, takeaways, and references.',
        function: 'pattern_explanation_and_application',
        flow: chapterFlow,
        start_line: 1,
        end_line: lines.length,
        title_en: 'Chapter 1: Prompt Chaining',
        title_zh: '第 1 章：提示词链',
        sections,
      }
    : {
        ...chapterBase,
        start_line: 1,
        end_line: lines.length,
        title_en: 'Chapter 1: Prompt Chaining',
        title_zh: '第 1 章：提示词链',
        sections,
      };

  const document = {
    status: 'ok',
    document_id: 'chapter1-prompt-chaining',
    source_path: SOURCE_REL,
    source_sha256: createHash('sha256').update(lines.join('\n')).digest('hex'),
    format: 'markdown',
    language_mode: 'bilingual',
    segmentation_strategy: includeRollups
      ? 'scripted_markdown_structure_semantic_beats_and_rollups'
      : 'scripted_markdown_structure_semantic_beats',
    stats: {},
    book: {
      id: 'book01',
      title: null,
      chapters: [chapter],
    },
    validation: {
      coverage: 'unknown',
      errors: [],
      warnings: [],
    },
  };
  document.stats = computeStats(document);
  return document;
}

function buildSection(sectionDef, lines, includeRollups) {
  const beats = (sectionDef.beats || []).map((beatDef, index) =>
    buildBeat(sectionDef, beatDef, index + 1, lines)
  );
  const referenceBlocks = (sectionDef.reference_blocks || []).map((refDef) =>
    buildReferenceBlock(sectionDef, refDef, lines)
  );
  const rollupUnits = [...beats, ...referenceBlocks];
  const flow = rollupUnits.map((unit) => unit.function).join(' -> ');
  const titleParts = splitBilingualTitle(sectionDef.title);
  const base = {
    id: sectionDef.id,
    chapter_id: 'c01',
    title: sectionDef.title,
  };
  const section = includeRollups
    ? {
        ...base,
        summary: sectionDef.summary,
        function: sectionDef.function,
        flow,
        start_line: sectionDef.start_line,
        end_line: sectionDef.end_line,
        title_en: titleParts.title_en,
        title_zh: titleParts.title_zh,
        subsections: [],
        beats,
      }
    : {
        ...base,
        start_line: sectionDef.start_line,
        end_line: sectionDef.end_line,
        title_en: titleParts.title_en,
        title_zh: titleParts.title_zh,
        subsections: [],
        beats,
      };
  if (referenceBlocks.length) section.reference_blocks = referenceBlocks;
  return section;
}

function buildBeat(sectionDef, beatDef, index, lines) {
  const id = `${sectionDef.id}-b${String(index).padStart(2, '0')}`;
  const source = sourceForRanges(lines, beatDef.ranges);
  const flags = artifactFlags(source);
  const beat = {
    id,
    book_id: 'book01',
    chapter_id: 'c01',
    section_id: sectionDef.id,
    subsection_id: null,
    title: beatDef.title,
    summary: beatDef.summary,
    function: beatDef.function,
    start_line: beatDef.ranges[0][0],
    end_line: beatDef.ranges.at(-1)[1],
    line_ranges: beatDef.ranges,
    source_markdown: source,
    boundary_reason: beatDef.boundary_reason,
    ...flags,
  };
  addOptionalAlignmentFields(beat, beatDef);
  addOptionalTitleParts(beat, beatDef.title);
  return beat;
}

function buildReferenceBlock(sectionDef, refDef, lines) {
  const source = sourceForRanges(lines, refDef.ranges);
  return {
    id: refDef.id,
    book_id: 'book01',
    chapter_id: 'c01',
    section_id: sectionDef.id,
    subsection_id: null,
    title: refDef.title,
    summary: refDef.summary,
    function: refDef.function,
    start_line: refDef.ranges[0][0],
    end_line: refDef.ranges.at(-1)[1],
    line_ranges: refDef.ranges,
    source_markdown: source,
    boundary_reason: refDef.boundary_reason,
    contains_code: false,
    contains_json: false,
    contains_table: false,
    contains_image: false,
    contains_references: true,
  };
}

function addOptionalAlignmentFields(unit, def) {
  if (def.source_is_contiguous === false) {
    unit.source_is_contiguous = false;
    unit.alignment_confidence = def.alignment_confidence || 'medium';
  }
  if (def.text_en_lines) unit.text_en_lines = def.text_en_lines;
  if (def.text_zh_lines) unit.text_zh_lines = def.text_zh_lines;
}

function addOptionalTitleParts(unit, title) {
  const parts = splitBilingualTitle(title);
  if (parts.title_en) unit.title_en = parts.title_en;
  if (parts.title_zh) unit.title_zh = parts.title_zh;
}

function computeStats(document) {
  const sections = document.book.chapters.flatMap((chapter) => chapter.sections);
  const beats = sections.flatMap((section) => [
    ...section.beats,
    ...section.subsections.flatMap((subsection) => subsection.beats || []),
  ]);
  const referenceBlocks = sections.flatMap((section) => section.reference_blocks || []);
  return {
    books: 1,
    chapters: document.book.chapters.length,
    sections: sections.length,
    subsections: sections.reduce((sum, section) => sum + section.subsections.length, 0),
    beats: beats.length,
    reference_blocks: referenceBlocks.length,
  };
}

function validateDocument(document, lines, { requireRollups }) {
  const errors = [];
  const warnings = [];
  const units = allContentUnits(document);
  const headingLines = scanHeadingLines(lines);
  const expected = new Set();
  for (let lineNo = 1; lineNo <= lines.length; lineNo += 1) {
    if (lines[lineNo - 1].trim() && !headingLines.has(lineNo)) expected.add(lineNo);
  }

  const coveredBy = new Map();
  for (const unit of units) {
    for (const field of [
      'id',
      'summary',
      'function',
      'start_line',
      'end_line',
      'line_ranges',
      'source_markdown',
    ]) {
      if (unit[field] === undefined || unit[field] === null || unit[field] === '') {
        errors.push(`${unit.id || '<unknown>'} is missing ${field}.`);
      }
    }

    const expectedSource = sourceForRanges(lines, unit.line_ranges);
    if (unit.source_markdown !== expectedSource) {
      errors.push(`${unit.id} source_markdown does not match line_ranges.`);
    }

    const isContiguous = unit.line_ranges.length === 1;
    if (!isContiguous && unit.source_is_contiguous !== false) {
      errors.push(`${unit.id} has non-contiguous ranges but is not marked source_is_contiguous=false.`);
    }
    if (!isContiguous && !unit.alignment_confidence) {
      errors.push(`${unit.id} has non-contiguous ranges without alignment_confidence.`);
    }

    for (const [start, end] of unit.line_ranges) {
      if (start > end) errors.push(`${unit.id} has invalid range ${start}-${end}.`);
      for (let lineNo = start; lineNo <= end; lineNo += 1) {
        if (!lines[lineNo - 1]?.trim() || headingLines.has(lineNo)) continue;
        if (coveredBy.has(lineNo)) {
          errors.push(`Line ${lineNo} is covered by both ${coveredBy.get(lineNo)} and ${unit.id}.`);
        }
        coveredBy.set(lineNo, unit.id);
      }
    }
  }

  const missing = [...expected].filter((lineNo) => !coveredBy.has(lineNo));
  if (missing.length) errors.push(`Missing non-heading source lines: ${compactLineList(missing)}.`);

  validateCodeFenceIntegrity(lines, coveredBy, errors);
  validateHierarchy(document, errors);
  if (requireRollups) validateRollups(document, errors);

  return {
    coverage: errors.some((error) => error.startsWith('Missing') || error.startsWith('Line '))
      ? 'incomplete'
      : 'complete',
    errors,
    warnings,
  };
}

function allContentUnits(document) {
  const units = [];
  for (const chapter of document.book.chapters) {
    for (const section of chapter.sections) {
      units.push(...section.beats);
      for (const subsection of section.subsections) units.push(...(subsection.beats || []));
      units.push(...(section.reference_blocks || []));
    }
  }
  return units;
}

function validateHierarchy(document, errors) {
  document.book.chapters.forEach((chapter, chapterIndex) => {
    const expectedChapterId = `c${String(chapterIndex + 1).padStart(2, '0')}`;
    if (chapter.id !== expectedChapterId) errors.push(`Chapter ${chapter.id} should be ${expectedChapterId}.`);
    chapter.sections.forEach((section, sectionIndex) => {
      const expectedSectionId = `${chapter.id}-s${String(sectionIndex + 1).padStart(2, '0')}`;
      if (section.id !== expectedSectionId) errors.push(`Section ${section.id} should be ${expectedSectionId}.`);
      section.beats.forEach((beat, beatIndex) => {
        const expectedBeatId = `${section.id}-b${String(beatIndex + 1).padStart(2, '0')}`;
        if (beat.id !== expectedBeatId) errors.push(`Beat ${beat.id} should be ${expectedBeatId}.`);
      });
      (section.reference_blocks || []).forEach((reference, referenceIndex) => {
        const expectedRefId = `${section.id}-ref${String(referenceIndex + 1).padStart(2, '0')}`;
        if (reference.id !== expectedRefId) errors.push(`Reference ${reference.id} should be ${expectedRefId}.`);
      });
    });
  });
}

function validateRollups(document, errors) {
  if ('summary' in document.book || 'function' in document.book || 'flow' in document.book) {
    errors.push('Single-chapter book must not include book-level summary, function, or flow.');
  }
  for (const chapter of document.book.chapters) {
    for (const field of ['summary', 'function', 'flow']) {
      if (!chapter[field]) errors.push(`Chapter ${chapter.id} is missing ${field}.`);
    }
    const expectedChapterFlow = chapter.sections.map((section) => section.function).join(' -> ');
    if (chapter.flow !== expectedChapterFlow) {
      errors.push(`Chapter ${chapter.id} flow does not match section functions.`);
    }
    for (const section of chapter.sections) {
      for (const field of ['summary', 'function']) {
        if (!section[field]) errors.push(`Section ${section.id} is missing ${field}.`);
      }
      const expectedFlow = [
        ...section.beats,
        ...section.subsections.flatMap((subsection) => subsection.beats || []),
        ...(section.reference_blocks || []),
      ]
        .map((unit) => unit.function)
        .join(' -> ');
      if (section.flow !== expectedFlow) {
        errors.push(`Section ${section.id} flow does not match content unit functions.`);
      }
    }
  }
}

function validateCodeFenceIntegrity(lines, coveredBy, errors) {
  for (const [start, end] of scanCodeFenceSpans(lines)) {
    const ids = new Set();
    for (let lineNo = start; lineNo <= end; lineNo += 1) {
      if (lines[lineNo - 1].trim() && coveredBy.has(lineNo)) ids.add(coveredBy.get(lineNo));
    }
    if (ids.size > 1) {
      errors.push(`Code fence ${start}-${end} is split across content units: ${[...ids].join(', ')}.`);
    }
  }
}

function buildDiffReport(scripted, finalDocument) {
  const scriptedBeats = scripted.book.chapters.flatMap((chapter) =>
    chapter.sections.flatMap((section) => [
      ...section.beats,
      ...section.subsections.flatMap((subsection) => subsection.beats || []),
    ])
  );
  const finalUnits = allContentUnits(finalDocument);
  const finalRangeKeys = new Set(finalUnits.map((unit) => rangeKey(unit.line_ranges)));
  const keptCount = scriptedBeats.filter((beat) => finalRangeKeys.has(rangeKey(beat.line_ranges))).length;
  const finalStats = finalDocument.stats;
  const lines = [];

  lines.push('# Chapter 1 Segmentation Diff');
  lines.push('');
  lines.push(`- Scripted structural file: \`${SCRIPTED_REL}\``);
  lines.push(`- Validated final file: \`${FINAL_REL}\``);
  lines.push(`- LLM refinement draft: \`${LLM_REL}\``);
  lines.push(`- Reproducibility script: \`${SCRIPT_REL}\``);
  lines.push(`- Rebuild command: \`node ${SCRIPT_REL}\``);
  lines.push('');
  lines.push('## Stats');
  lines.push('');
  lines.push('| Stage | Sections | Beats | Reference blocks |');
  lines.push('| --- | ---: | ---: | ---: |');
  lines.push(
    `| Scripted | ${scripted.stats.sections} | ${scripted.stats.beats} | ${scripted.stats.reference_blocks} |`
  );
  lines.push(
    `| Final | ${finalStats.sections} | ${finalStats.beats} | ${finalStats.reference_blocks} |`
  );
  lines.push('');
  lines.push(`- Kept scripted beat ranges: ${keptCount}`);
  lines.push(`- Split scripted beats: ${CHANGE_LOG.length}`);
  lines.push('- Merged scripted beats: 0');
  lines.push('- Non-contiguous bilingual alignments: 2');
  lines.push('- Reference beat converted to reference block: 1');
  lines.push('');
  lines.push('## Split Beats');
  lines.push('');
  for (const change of CHANGE_LOG) {
    lines.push(
      `- \`${change.oldId}\` ${change.oldRange} -> ${change.newRanges
        .map((item) => `\`${item}\``)
        .join(', ')}. ${change.reason}`
    );
  }
  lines.push('');
  lines.push('## Non-contiguous Alignments');
  lines.push('');
  lines.push(
    '- `c01-s03-b02` aligns the English setup/install span `249-255` with the delayed Chinese provider note on line `306`.'
  );
  lines.push(
    '- `c01-s03-b03` keeps the Python code fence intact on `257-304` and aligns it with the delayed Chinese code explanation on line `308`.'
  );
  lines.push('');
  lines.push('## Semantic Metadata');
  lines.push('');
  lines.push(
    '- Replaced heuristic scripted beat summaries/functions with content-specific summaries and article-function labels.'
  );
  lines.push(
    '- Added section and chapter rollups. Section flows are generated from beat/reference functions in source order; the chapter flow is generated from section functions.'
  );
  lines.push(
    '- Omitted book-level summary/function/flow because this artifact contains a single chapter.'
  );
  lines.push('');
  return `${lines.join('\n')}\n`;
}

function splitLines(sourceText) {
  const normalized = sourceText.replace(/\r\n/g, '\n');
  if (normalized.endsWith('\n')) return normalized.slice(0, -1).split('\n');
  return normalized.split('\n');
}

function sourceForRanges(lines, ranges) {
  return ranges
    .map(([start, end]) => lines.slice(start - 1, end).join('\n'))
    .join('\n\n');
}

function artifactFlags(source) {
  const fenceInfos = [...source.matchAll(/```([^\n]*)\n[\s\S]*?```/g)].map((match) =>
    match[1].trim().toLowerCase()
  );
  const tableLines = source.split('\n').filter((line) => line.trim().startsWith('|'));
  return {
    contains_code: fenceInfos.length > 0,
    contains_json:
      fenceInfos.some((info) => info.includes('json')) || /(^|\n)\s*[\[{]\s*(\n|$)/.test(source),
    contains_table: tableLines.length >= 2 && tableLines.some((line) => line.includes('---')),
    contains_image: /!\[[^\]]*\](?:\([^)]+\)|\[[^\]]*\])/.test(source),
    contains_references: /(^|\n)\s*\[[^\]]+\]:\s+\S+/.test(source) || /https?:\/\//.test(source),
  };
}

function splitBilingualTitle(title) {
  if (!title || !title.includes(' / ')) return { title_en: undefined, title_zh: undefined };
  const [first, second] = title.split(' / ', 2);
  const firstHasCjk = /[\u4e00-\u9fff]/.test(first);
  const secondHasCjk = /[\u4e00-\u9fff]/.test(second);
  if (!firstHasCjk && secondHasCjk) return { title_en: first, title_zh: second };
  if (firstHasCjk && !secondHasCjk) return { title_en: second, title_zh: first };
  return { title_en: first, title_zh: second };
}

function scanHeadingLines(lines) {
  const headingLines = new Set();
  let inFence = false;
  let fenceMarker = '';
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const fenceMatch = line.match(/^\s*(```+|~~~+)/);
    if (fenceMatch) {
      const marker = fenceMatch[1][0];
      if (!inFence) {
        inFence = true;
        fenceMarker = marker;
      } else if (marker === fenceMarker) {
        inFence = false;
        fenceMarker = '';
      }
      continue;
    }
    if (!inFence && /^#{1,6}\s+/.test(line)) headingLines.add(index + 1);
  }
  return headingLines;
}

function scanCodeFenceSpans(lines) {
  const spans = [];
  let inFence = false;
  let marker = '';
  let start = 0;
  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^\s*(```+|~~~+)/);
    if (!match) continue;
    const current = match[1][0];
    if (!inFence) {
      inFence = true;
      marker = current;
      start = index + 1;
    } else if (current === marker) {
      spans.push([start, index + 1]);
      inFence = false;
      marker = '';
      start = 0;
    }
  }
  return spans;
}

function rangeKey(ranges) {
  return ranges.map(([start, end]) => `${start}-${end}`).join('+');
}

function compactLineList(lineNumbers, limit = 30) {
  if (lineNumbers.length <= limit) return lineNumbers.join(', ');
  return `${lineNumbers.slice(0, limit).join(', ')}, ... (${lineNumbers.length} total)`;
}

async function writeJson(filePath, payload) {
  await writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
