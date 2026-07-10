#!/usr/bin/env python3
"""Deterministic Markdown structure segmentation for the text-segmentation skill.

This script performs the token-expensive first pass without an LLM:
Markdown block protection, bilingual heading pairing, hierarchy mapping,
coarse beat boundary selection, artifact flags, and structural validation.
The summary/function fields are heuristic placeholders intended for a later
small LLM pass when higher semantic quality is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
PSEUDO_RE = re.compile(r"^[ \t]*\*\*(?P<label>[^*\n]{2,160}?[：:])\*\*")
CHAPTER_RE = re.compile(
    r"(\bchapter\s+\d+\b|"
    r"\u7b2c\s*\d+\s*\u7ae0|"
    r"\u7b2c\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d"
    r"\u5341\u767e\u96f6\u3007\u4e24]+\s*\u7ae0)",
    re.IGNORECASE,
)
LIST_RE = re.compile(r"^[ \t]*(?:[-+*]|\d+[.)]|\d+\\\.)\s+")
LINK_REFERENCE_RE = re.compile(r"^[ \t]*\[[^\]]+\]:\s+\S+")
URL_RE = re.compile(r"https?://")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    start_line: int
    end_line: int
    title_en: str | None = None
    title_zh: str | None = None


@dataclass(frozen=True)
class PseudoBoundary:
    line_no: int
    label: str


@dataclass(frozen=True)
class TextBlock:
    start_line: int
    end_line: int
    text: str


def read_markdown(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def has_latin(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text))


def language_mode(lines: list[str]) -> str:
    text = "\n".join(lines)
    if has_cjk(text) and has_latin(text):
        return "bilingual"
    if has_cjk(text):
        return "monolingual"
    return "monolingual"


def is_blank_range(lines: list[str], start_line: int, end_line: int) -> bool:
    if start_line > end_line:
        return True
    return all(not lines[i - 1].strip() for i in range(start_line, end_line + 1))


def strip_heading_markup(title: str) -> str:
    title = title.strip()
    title = re.sub(r"[ \t]+#+$", "", title).strip()
    return title


def scan_headings(lines: list[str]) -> list[Heading]:
    headings: list[Heading] = []
    fence_marker: str | None = None
    fence_len = 0

    for idx, line in enumerate(lines, start=1):
        if fence_marker:
            stripped = line.lstrip()
            if stripped.startswith(fence_marker * fence_len):
                fence_marker = None
                fence_len = 0
            continue

        fence_match = FENCE_OPEN_RE.match(line)
        if fence_match:
            fence = fence_match.group(1)
            fence_marker = fence[0]
            fence_len = len(fence)
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            headings.append(
                Heading(
                    level=len(heading_match.group(1)),
                    title=strip_heading_markup(heading_match.group(2)),
                    start_line=idx,
                    end_line=idx,
                )
            )

    return headings


def merge_bilingual_headings(lines: list[str], headings: list[Heading]) -> list[Heading]:
    merged: list[Heading] = []
    idx = 0
    while idx < len(headings):
        current = headings[idx]
        nxt = headings[idx + 1] if idx + 1 < len(headings) else None
        if (
            nxt
            and current.level == nxt.level
            and is_blank_range(lines, current.end_line + 1, nxt.start_line - 1)
            and has_cjk(current.title) != has_cjk(nxt.title)
        ):
            title_en = current.title if not has_cjk(current.title) else nxt.title
            title_zh = current.title if has_cjk(current.title) else nxt.title
            merged.append(
                Heading(
                    level=current.level,
                    title=f"{title_en} / {title_zh}",
                    start_line=current.start_line,
                    end_line=nxt.end_line,
                    title_en=title_en,
                    title_zh=title_zh,
                )
            )
            idx += 2
            continue
        merged.append(current)
        idx += 1
    return merged


def heading_lines(headings: list[Heading]) -> set[int]:
    excluded: set[int] = set()
    for heading in headings:
        excluded.update(range(heading.start_line, heading.end_line + 1))
    return excluded


def line_text(lines: list[str], start_line: int, end_line: int) -> str:
    if start_line > end_line:
        return ""
    return "\n".join(lines[start_line - 1 : end_line])


def trim_span(lines: list[str], start_line: int, end_line: int) -> tuple[int, int] | None:
    while start_line <= end_line and not lines[start_line - 1].strip():
        start_line += 1
    while end_line >= start_line and not lines[end_line - 1].strip():
        end_line -= 1
    if start_line > end_line:
        return None
    return start_line, end_line


def explicit_chapter(heading: Heading) -> bool:
    return bool(CHAPTER_RE.search(heading.title))


def clean_inline_markdown(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("\\.", ".")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def first_meaningful_line(source: str, prefer_latin: bool = True) -> str:
    candidates: list[str] = []
    for raw in source.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            continue
        if LINK_REFERENCE_RE.match(stripped):
            continue
        if stripped.startswith("!") and "]" in stripped:
            continue
        candidates.append(clean_inline_markdown(stripped))

    if prefer_latin:
        for candidate in candidates:
            if has_latin(candidate) and not has_cjk(candidate):
                return candidate
    return candidates[0] if candidates else ""


def truncate_text(text: str, limit: int = 180) -> str:
    text = clean_inline_markdown(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def title_parts(title: str | None) -> tuple[str | None, str | None]:
    if not title:
        return None, None
    if " / " not in title:
        if has_cjk(title):
            return None, title
        return title, None
    first, second = title.split(" / ", 1)
    if has_cjk(first) and not has_cjk(second):
        return second.strip(), first.strip()
    if has_cjk(second) and not has_cjk(first):
        return first.strip(), second.strip()
    return first.strip(), second.strip()


def make_summary(source: str, title: str | None = None) -> str:
    lead = first_meaningful_line(source)
    if lead:
        return f"Covers: {truncate_text(lead)}"
    if title:
        return f"Covers {truncate_text(title, 120)}."
    return "Covers this Markdown segment."


def infer_function(
    section_title: str | None,
    beat_title: str | None,
    source: str,
    contains: dict[str, bool],
) -> str:
    joined = " ".join(part for part in [section_title, beat_title, source[:500]] if part)
    lower = joined.lower()

    if contains["contains_references"] or "reference" in lower or "\u53c2\u8003" in joined:
        return "references"
    if contains["contains_image"] or "visual summary" in lower or "\u53ef\u89c6\u5316" in joined:
        return "visual_summary"
    if contains["contains_json"] or "structured output" in lower:
        return "structured_output_example"
    if contains["contains_code"]:
        if "pip install" in lower:
            return "setup_instruction"
        return "code_example"
    if "json" in lower:
        return "structured_output_example"
    if "conclusion" in lower or "\u7ed3\u8bba" in joined:
        return "conclusion"
    if "key takeaways" in lower or "\u5173\u952e\u8981\u70b9" in joined:
        return "conclusion"
    if "limitation" in lower or "\u5c40\u9650" in joined or "\u95ee\u9898\u80cc\u666f" in joined:
        return "limitation"
    if "why" in lower or "solution" in lower or "reliability" in lower or "\u89e3\u51b3" in joined:
        return "solution_explanation"
    if "what" in lower or "overview" in lower or "\u6982\u8ff0" in joined:
        return "concept_overview"
    if "rule of thumb" in lower or "\u5b9e\u8df5\u5efa\u8bae" in joined:
        return "use_case"
    if "application" in lower or "use case" in lower or "\u7528\u4f8b" in joined:
        return "use_case"
    if "context engineering" in lower and "prompt engineering" in lower:
        return "comparison"
    if re.search(r"\*\*\d+(?:\\)?[.)]", source):
        return "use_case"
    return "concept_overview"


def scan_code_fences(lines: list[str]) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    fence_marker: str | None = None
    fence_len = 0
    fence_info = ""
    fence_start = 0

    for idx, line in enumerate(lines, start=1):
        if fence_marker:
            stripped = line.lstrip()
            if stripped.startswith(fence_marker * fence_len):
                spans.append((fence_start, idx, fence_info))
                fence_marker = None
                fence_len = 0
                fence_info = ""
            continue

        fence_match = FENCE_OPEN_RE.match(line)
        if fence_match:
            fence = fence_match.group(1)
            fence_marker = fence[0]
            fence_len = len(fence)
            fence_info = fence_match.group(2).strip().lower()
            fence_start = idx

    if fence_marker:
        spans.append((fence_start, len(lines), fence_info))
    return spans


def artifact_flags(lines: list[str], start_line: int, end_line: int) -> dict[str, bool]:
    source = line_text(lines, start_line, end_line)
    fence_spans = scan_code_fences(lines[start_line - 1 : end_line])
    contains_code = bool(fence_spans)
    contains_json = any("json" in info for _, _, info in fence_spans)
    contains_json = contains_json or bool(re.search(r"(?m)^[ \t]*[\{\[]\s*$", source))
    table_lines = [ln for ln in source.splitlines() if ln.strip().startswith("|")]
    contains_table = len(table_lines) >= 2 and any("---" in ln for ln in table_lines)
    contains_image = bool(re.search(r"!\[[^\]]*\](?:\([^)]+\)|\[[^\]]*\])", source))
    contains_references = any(
        LINK_REFERENCE_RE.match(raw.strip()) or URL_RE.search(raw) for raw in source.splitlines()
    )
    return {
        "contains_code": contains_code,
        "contains_json": contains_json,
        "contains_table": contains_table,
        "contains_image": contains_image,
        "contains_references": contains_references,
    }


def find_pseudo_boundaries(lines: list[str], start_line: int, end_line: int) -> list[PseudoBoundary]:
    candidates: list[PseudoBoundary] = []
    fence_marker: str | None = None
    fence_len = 0

    for line_no in range(start_line, end_line + 1):
        line = lines[line_no - 1]
        if fence_marker:
            stripped = line.lstrip()
            if stripped.startswith(fence_marker * fence_len):
                fence_marker = None
                fence_len = 0
            continue

        fence_match = FENCE_OPEN_RE.match(line)
        if fence_match:
            fence = fence_match.group(1)
            fence_marker = fence[0]
            fence_len = len(fence)
            continue

        pseudo_match = PSEUDO_RE.match(line)
        if pseudo_match:
            label = clean_inline_markdown(pseudo_match.group("label")).rstrip(":：").strip()
            candidates.append(PseudoBoundary(line_no=line_no, label=label))

    if not candidates:
        return []

    section_text = line_text(lines, start_line, end_line)
    bilingual = has_cjk(section_text) and has_latin(section_text)
    accepted: list[PseudoBoundary] = []
    for candidate in candidates:
        if bilingual and has_cjk(candidate.label) and accepted and not has_cjk(accepted[-1].label):
            continue
        accepted.append(candidate)
    return accepted


def blockify(lines: list[str], start_line: int, end_line: int) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    line_no = start_line

    while line_no <= end_line:
        while line_no <= end_line and not lines[line_no - 1].strip():
            line_no += 1
        if line_no > end_line:
            break

        fence_match = FENCE_OPEN_RE.match(lines[line_no - 1])
        if fence_match:
            fence = fence_match.group(1)
            marker = fence[0]
            fence_len = len(fence)
            block_start = line_no
            line_no += 1
            while line_no <= end_line:
                if lines[line_no - 1].lstrip().startswith(marker * fence_len):
                    line_no += 1
                    break
                line_no += 1
            blocks.append(TextBlock(block_start, line_no - 1, line_text(lines, block_start, line_no - 1)))
            continue

        block_start = line_no
        line_no += 1
        while line_no <= end_line and lines[line_no - 1].strip():
            if FENCE_OPEN_RE.match(lines[line_no - 1]):
                break
            line_no += 1
        blocks.append(TextBlock(block_start, line_no - 1, line_text(lines, block_start, line_no - 1)))

    return blocks


def pair_bilingual_blocks(blocks: list[TextBlock]) -> list[TextBlock]:
    paired: list[TextBlock] = []
    idx = 0
    while idx < len(blocks):
        current = blocks[idx]
        nxt = blocks[idx + 1] if idx + 1 < len(blocks) else None
        if nxt and has_cjk(current.text) != has_cjk(nxt.text):
            paired.append(
                TextBlock(
                    start_line=current.start_line,
                    end_line=nxt.end_line,
                    text=line_join_blocks([current, nxt]),
                )
            )
            idx += 2
            continue
        paired.append(current)
        idx += 1
    return paired


def line_join_blocks(blocks: list[TextBlock]) -> str:
    return "\n\n".join(block.text for block in blocks)


def split_span(
    lines: list[str],
    start_line: int,
    end_line: int,
    max_chars: int,
) -> list[tuple[int, int, str]]:
    trimmed = trim_span(lines, start_line, end_line)
    if not trimmed:
        return []
    start_line, end_line = trimmed
    source = line_text(lines, start_line, end_line)
    if len(source) <= max_chars:
        return [(start_line, end_line, "coarse_structural_span")]

    units = pair_bilingual_blocks(blockify(lines, start_line, end_line))
    chunks: list[tuple[int, int, str]] = []
    chunk_start: int | None = None
    chunk_end: int | None = None
    chunk_text_len = 0

    for unit in units:
        unit_len = len(unit.text)
        if chunk_start is not None and chunk_text_len + unit_len > max_chars:
            chunks.append((chunk_start, chunk_end or chunk_start, "max_chars_paragraph_group"))
            chunk_start = None
            chunk_end = None
            chunk_text_len = 0

        if chunk_start is None:
            chunk_start = unit.start_line
        chunk_end = unit.end_line
        chunk_text_len += unit_len

    if chunk_start is not None:
        chunks.append((chunk_start, chunk_end or chunk_start, "max_chars_paragraph_group"))

    return chunks


def make_beat(
    lines: list[str],
    beat_id: str,
    book_id: str,
    chapter_id: str,
    section_id: str,
    subsection_id: str | None,
    section_title: str | None,
    title: str | None,
    start_line: int,
    end_line: int,
    boundary_reason: str,
) -> dict[str, Any]:
    source = line_text(lines, start_line, end_line)
    contains = artifact_flags(lines, start_line, end_line)
    title_en, title_zh = title_parts(title)
    beat: dict[str, Any] = {
        "id": beat_id,
        "book_id": book_id,
        "chapter_id": chapter_id,
        "section_id": section_id,
        "subsection_id": subsection_id,
        "title": title,
        "summary": make_summary(source, title),
        "summary_status": "heuristic_needs_llm_review",
        "function": infer_function(section_title, title, source, contains),
        "function_status": "heuristic_needs_llm_review",
        "start_line": start_line,
        "end_line": end_line,
        "line_ranges": [[start_line, end_line]],
        "source_markdown": source,
        "boundary_reason": boundary_reason,
        **contains,
    }
    if title_en:
        beat["title_en"] = title_en
    if title_zh:
        beat["title_zh"] = title_zh
    return beat


def build_beats(
    lines: list[str],
    book_id: str,
    chapter_id: str,
    section_id: str,
    subsection_id: str | None,
    section_title: str | None,
    parent_title: str | None,
    start_line: int,
    end_line: int,
    max_chars: int,
) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []
    if start_line > end_line:
        return beats

    pseudo_boundaries = find_pseudo_boundaries(lines, start_line, end_line)
    spans: list[tuple[int, int, str, str | None]] = []

    if pseudo_boundaries:
        first = pseudo_boundaries[0]
        for span_start, span_end, reason in split_span(lines, start_line, first.line_no - 1, max_chars):
            spans.append((span_start, span_end, reason, parent_title))
        for idx, boundary in enumerate(pseudo_boundaries):
            next_start = pseudo_boundaries[idx + 1].line_no if idx + 1 < len(pseudo_boundaries) else end_line + 1
            pseudo_end = next_start - 1
            pseudo_source = line_text(lines, boundary.line_no, pseudo_end)
            if len(pseudo_source) <= max_chars:
                trimmed = trim_span(lines, boundary.line_no, pseudo_end)
                if trimmed:
                    spans.append((trimmed[0], trimmed[1], "pseudo_subsection", boundary.label))
            else:
                for part_idx, (span_start, span_end, reason) in enumerate(
                    split_span(lines, boundary.line_no, pseudo_end, max_chars),
                    start=1,
                ):
                    title = boundary.label if part_idx == 1 else f"{boundary.label} Part {part_idx}"
                    spans.append((span_start, span_end, reason, title))
    else:
        for span_start, span_end, reason in split_span(lines, start_line, end_line, max_chars):
            spans.append((span_start, span_end, reason, parent_title))

    beat_prefix = f"{subsection_id}-b" if subsection_id else f"{section_id}-b"
    for idx, (span_start, span_end, reason, title) in enumerate(spans, start=1):
        beat_title = title
        if title == parent_title and len(spans) > 1:
            beat_title = f"{parent_title} Part {idx}" if parent_title else f"Part {idx}"
        beats.append(
            make_beat(
                lines=lines,
                beat_id=f"{beat_prefix}{idx:02d}",
                book_id=book_id,
                chapter_id=chapter_id,
                section_id=section_id,
                subsection_id=subsection_id,
                section_title=section_title,
                title=beat_title,
                start_line=span_start,
                end_line=span_end,
                boundary_reason=reason,
            )
        )
    return beats


def headings_in_span(headings: list[Heading], start_line: int, end_line: int) -> list[Heading]:
    return [heading for heading in headings if start_line <= heading.start_line <= end_line]


def next_boundary_start(boundaries: list[Heading], idx: int, fallback_end: int) -> int:
    return boundaries[idx + 1].start_line - 1 if idx + 1 < len(boundaries) else fallback_end


def make_section(
    lines: list[str],
    headings: list[Heading],
    book_id: str,
    chapter_id: str,
    section_id: str,
    title: str | None,
    heading: Heading | None,
    start_line: int,
    end_line: int,
    max_chars: int,
    inferred: bool = False,
) -> dict[str, Any]:
    section_title_en, section_title_zh = title_parts(title)
    section: dict[str, Any] = {
        "id": section_id,
        "chapter_id": chapter_id,
        "title": title,
        "start_line": start_line,
        "end_line": end_line,
        "subsections": [],
        "beats": [],
    }
    if inferred:
        section["inferred"] = True
    if section_title_en:
        section["title_en"] = section_title_en
    if section_title_zh:
        section["title_zh"] = section_title_zh

    body_start = (heading.end_line + 1) if heading else start_line
    body_end = end_line
    inner_headings = headings_in_span(headings, body_start, body_end)
    lower_headings = [item for item in inner_headings if heading is None or item.level > heading.level]

    if lower_headings:
        subsection_level = min(item.level for item in lower_headings)
        subsection_headings = [item for item in lower_headings if item.level == subsection_level]
        preface_end = subsection_headings[0].start_line - 1
        section["beats"] = build_beats(
            lines,
            book_id,
            chapter_id,
            section_id,
            None,
            title,
            title,
            body_start,
            preface_end,
            max_chars,
        )
        for ss_idx, subsection_heading in enumerate(subsection_headings, start=1):
            subsection_id = f"{section_id}-ss{ss_idx:02d}"
            subsection_end = next_boundary_start(subsection_headings, ss_idx - 1, body_end)
            subsection_title_en, subsection_title_zh = title_parts(subsection_heading.title)
            subsection: dict[str, Any] = {
                "id": subsection_id,
                "section_id": section_id,
                "title": subsection_heading.title,
                "start_line": subsection_heading.start_line,
                "end_line": subsection_end,
                "beats": build_beats(
                    lines,
                    book_id,
                    chapter_id,
                    section_id,
                    subsection_id,
                    title,
                    subsection_heading.title,
                    subsection_heading.end_line + 1,
                    subsection_end,
                    max_chars,
                ),
            }
            if subsection_title_en:
                subsection["title_en"] = subsection_title_en
            if subsection_title_zh:
                subsection["title_zh"] = subsection_title_zh
            section["subsections"].append(subsection)
    else:
        section["beats"] = build_beats(
            lines,
            book_id,
            chapter_id,
            section_id,
            None,
            title,
            title,
            body_start,
            body_end,
            max_chars,
        )

    return section


def build_sections(
    lines: list[str],
    headings: list[Heading],
    book_id: str,
    chapter_id: str,
    chapter_heading: Heading | None,
    chapter_start: int,
    chapter_end: int,
    max_chars: int,
) -> list[dict[str, Any]]:
    body_start = (chapter_heading.end_line + 1) if chapter_heading else chapter_start
    body_end = chapter_end
    chapter_level = chapter_heading.level if chapter_heading else 0
    inner_headings = [
        item
        for item in headings_in_span(headings, body_start, body_end)
        if item.level > chapter_level
    ]

    sections: list[dict[str, Any]] = []
    if inner_headings:
        section_level = min(item.level for item in inner_headings)
        section_headings = [item for item in inner_headings if item.level == section_level]

        preface_trimmed = trim_span(lines, body_start, section_headings[0].start_line - 1)
        if preface_trimmed:
            section_id = f"{chapter_id}-s{len(sections) + 1:02d}"
            sections.append(
                make_section(
                    lines,
                    headings,
                    book_id,
                    chapter_id,
                    section_id,
                    None,
                    None,
                    preface_trimmed[0],
                    preface_trimmed[1],
                    max_chars,
                    inferred=True,
                )
            )

        first_section_number = len(sections) + 1
        for local_idx, section_heading in enumerate(section_headings):
            section_id = f"{chapter_id}-s{first_section_number + local_idx:02d}"
            section_end = next_boundary_start(section_headings, local_idx, body_end)
            sections.append(
                make_section(
                    lines,
                    headings,
                    book_id,
                    chapter_id,
                    section_id,
                    section_heading.title,
                    section_heading,
                    section_heading.start_line,
                    section_end,
                    max_chars,
                )
            )
    else:
        trimmed = trim_span(lines, body_start, body_end)
        if trimmed:
            sections.append(
                make_section(
                    lines,
                    headings,
                    book_id,
                    chapter_id,
                    f"{chapter_id}-s01",
                    None,
                    None,
                    trimmed[0],
                    trimmed[1],
                    max_chars,
                    inferred=True,
                )
            )

    return sections


def determine_chapters(lines: list[str], headings: list[Heading]) -> tuple[str | None, list[tuple[Heading | None, int, int]]]:
    if not headings:
        return None, [(None, 1, len(lines))]

    explicit = [heading for heading in headings if explicit_chapter(heading)]
    h1_headings = [heading for heading in headings if heading.level == 1]

    if len(h1_headings) == 1 and not explicit_chapter(h1_headings[0]):
        lower_explicit = [heading for heading in explicit if heading.level > h1_headings[0].level]
        if lower_explicit:
            return h1_headings[0].title, chapter_boundaries(lower_explicit, lines)

    if explicit:
        return None, chapter_boundaries(explicit, lines)

    if h1_headings:
        return None, chapter_boundaries(h1_headings, lines)

    return None, [(None, 1, len(lines))]


def chapter_boundaries(chapter_headings: list[Heading], lines: list[str]) -> list[tuple[Heading | None, int, int]]:
    boundaries: list[tuple[Heading | None, int, int]] = []
    for idx, heading in enumerate(chapter_headings):
        end_line = chapter_headings[idx + 1].start_line - 1 if idx + 1 < len(chapter_headings) else len(lines)
        boundaries.append((heading, heading.start_line, end_line))
    return boundaries


def build_document(source_path: Path, lines: list[str], max_chars: int) -> dict[str, Any]:
    raw_headings = scan_headings(lines)
    headings = merge_bilingual_headings(lines, raw_headings)
    book_title, chapter_specs = determine_chapters(lines, headings)
    book_id = "book01"
    chapters: list[dict[str, Any]] = []

    for chapter_idx, (chapter_heading, chapter_start, chapter_end) in enumerate(chapter_specs, start=1):
        chapter_id = f"c{chapter_idx:02d}"
        chapter_title = chapter_heading.title if chapter_heading else None
        chapter_title_en, chapter_title_zh = title_parts(chapter_title)
        chapter: dict[str, Any] = {
            "id": chapter_id,
            "book_id": book_id,
            "title": chapter_title,
            "start_line": chapter_start,
            "end_line": chapter_end,
            "sections": build_sections(
                lines,
                headings,
                book_id,
                chapter_id,
                chapter_heading,
                chapter_start,
                chapter_end,
                max_chars,
            ),
        }
        if chapter_heading is None:
            chapter["inferred"] = True
        if chapter_title_en:
            chapter["title_en"] = chapter_title_en
        if chapter_title_zh:
            chapter["title_zh"] = chapter_title_zh
        chapters.append(chapter)

    output: dict[str, Any] = {
        "status": "ok",
        "document_id": source_path.stem,
        "source_path": str(source_path),
        "source_sha256": hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest(),
        "format": "markdown",
        "language_mode": language_mode(lines),
        "segmentation_strategy": "scripted_markdown_structure_coarse_beats",
        "book": {
            "id": book_id,
            "title": book_title,
            "chapters": chapters,
        },
        "validation": {
            "coverage": "unknown",
            "errors": [],
            "warnings": [],
        },
    }
    update_stats(output)
    validation = validate_document(output, lines, headings)
    output["validation"] = validation
    output["status"] = "ok" if not validation["errors"] else "invalid"
    update_stats(output)
    return output


def iter_sections(document: dict[str, Any]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for chapter in document["book"]["chapters"]:
        sections.extend(chapter.get("sections", []))
    return sections


def iter_subsections(document: dict[str, Any]) -> list[dict[str, Any]]:
    subsections: list[dict[str, Any]] = []
    for section in iter_sections(document):
        subsections.extend(section.get("subsections", []))
    return subsections


def iter_beats(document: dict[str, Any]) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []
    for section in iter_sections(document):
        beats.extend(section.get("beats", []))
        for subsection in section.get("subsections", []):
            beats.extend(subsection.get("beats", []))
    return beats


def update_stats(document: dict[str, Any]) -> None:
    beats = iter_beats(document)
    document["stats"] = {
        "books": 1,
        "chapters": len(document["book"]["chapters"]),
        "sections": len(iter_sections(document)),
        "subsections": len(iter_subsections(document)),
        "beats": len(beats),
        "reference_blocks": sum(1 for beat in beats if beat.get("contains_references")),
    }


def validate_document(document: dict[str, Any], lines: list[str], headings: list[Heading]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    excluded_headings = heading_lines(headings)
    beats = iter_beats(document)

    if not document["book"]["chapters"]:
        errors.append("No chapters were produced.")
    if not beats:
        errors.append("No beats were produced.")

    covered_once: dict[int, str] = {}
    duplicate_lines: list[int] = []
    for beat in beats:
        for key in ["id", "summary", "function", "start_line", "end_line", "line_ranges", "source_markdown"]:
            if key not in beat or beat[key] in (None, ""):
                errors.append(f"Beat {beat.get('id', '<unknown>')} is missing required field {key}.")

        expected_source = line_text(lines, beat["start_line"], beat["end_line"])
        if beat.get("source_markdown") != expected_source:
            errors.append(f"Beat {beat['id']} source_markdown does not match its line range.")

        for start_line, end_line in beat["line_ranges"]:
            if start_line > end_line:
                errors.append(f"Beat {beat['id']} has an invalid line range {start_line}-{end_line}.")
                continue
            for line_no in range(start_line, end_line + 1):
                if line_no in excluded_headings or not lines[line_no - 1].strip():
                    continue
                if line_no in covered_once:
                    duplicate_lines.append(line_no)
                covered_once[line_no] = beat["id"]

    expected_lines = {
        line_no
        for line_no, raw in enumerate(lines, start=1)
        if raw.strip() and line_no not in excluded_headings
    }
    covered_lines = set(covered_once)
    missing_lines = sorted(expected_lines - covered_lines)
    extra_lines = sorted(covered_lines - expected_lines)

    if missing_lines:
        errors.append(f"Missing non-heading source lines: {compact_line_list(missing_lines)}.")
    if extra_lines:
        errors.append(f"Covered unexpected source lines: {compact_line_list(extra_lines)}.")
    if duplicate_lines:
        errors.append(f"Duplicate coverage for source lines: {compact_line_list(sorted(set(duplicate_lines)))}.")

    validate_code_fence_integrity(lines, covered_once, errors)
    validate_hierarchy_ids(document, errors)

    if any(beat.get("summary_status") == "heuristic_needs_llm_review" for beat in beats):
        warnings.append("Beat summaries/functions are heuristic placeholders for a later semantic pass.")

    coverage = "complete" if not missing_lines and not extra_lines and not duplicate_lines else "incomplete"
    return {
        "coverage": coverage,
        "errors": errors,
        "warnings": warnings,
    }


def compact_line_list(line_numbers: list[int], limit: int = 30) -> str:
    if len(line_numbers) <= limit:
        return ", ".join(str(item) for item in line_numbers)
    shown = ", ".join(str(item) for item in line_numbers[:limit])
    return f"{shown}, ... ({len(line_numbers)} total)"


def validate_code_fence_integrity(lines: list[str], line_to_beat: dict[int, str], errors: list[str]) -> None:
    for start_line, end_line, _info in scan_code_fences(lines):
        beat_ids = {
            line_to_beat[line_no]
            for line_no in range(start_line, end_line + 1)
            if line_no in line_to_beat and lines[line_no - 1].strip()
        }
        if len(beat_ids) > 1:
            errors.append(
                f"Code fence lines {start_line}-{end_line} are split across beats: {sorted(beat_ids)}."
            )


def validate_hierarchy_ids(document: dict[str, Any], errors: list[str]) -> None:
    for c_idx, chapter in enumerate(document["book"]["chapters"], start=1):
        expected_chapter_id = f"c{c_idx:02d}"
        if chapter["id"] != expected_chapter_id:
            errors.append(f"Chapter ID {chapter['id']} should be {expected_chapter_id}.")
        for s_idx, section in enumerate(chapter.get("sections", []), start=1):
            expected_section_id = f"{chapter['id']}-s{s_idx:02d}"
            if section["id"] != expected_section_id:
                errors.append(f"Section ID {section['id']} should be {expected_section_id}.")
            for b_idx, beat in enumerate(section.get("beats", []), start=1):
                expected_beat_id = f"{section['id']}-b{b_idx:02d}"
                if beat["id"] != expected_beat_id:
                    errors.append(f"Beat ID {beat['id']} should be {expected_beat_id}.")
            for ss_idx, subsection in enumerate(section.get("subsections", []), start=1):
                expected_subsection_id = f"{section['id']}-ss{ss_idx:02d}"
                if subsection["id"] != expected_subsection_id:
                    errors.append(
                        f"Subsection ID {subsection['id']} should be {expected_subsection_id}."
                    )
                for b_idx, beat in enumerate(subsection.get("beats", []), start=1):
                    expected_beat_id = f"{subsection['id']}-b{b_idx:02d}"
                    if beat["id"] != expected_beat_id:
                        errors.append(f"Beat ID {beat['id']} should be {expected_beat_id}.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministically segment Markdown into hierarchical coarse-beat JSON."
    )
    parser.add_argument("source_path", type=Path, help="Markdown file to segment.")
    parser.add_argument("-o", "--output", type=Path, help="Write JSON to this path instead of stdout.")
    parser.add_argument(
        "--max-beat-chars",
        type=int,
        default=5000,
        help="Split structural spans larger than this many characters at paragraph/block boundaries.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when validation errors are present.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of pretty-printed JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.source_path.suffix.lower() not in {".md", ".markdown"}:
        unsupported = {
            "status": "unsupported",
            "reason": "text-segmentation only supports Markdown input.",
            "detected_format": args.source_path.suffix.lower().lstrip(".") or "unknown",
            "source_path": str(args.source_path),
            "operations_performed": [],
            "next_action": "terminate_without_segmentation",
        }
        payload = json.dumps(unsupported, ensure_ascii=False, indent=None if args.compact else 2)
        if args.output:
            args.output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        return 2 if args.check else 0

    lines = read_markdown(args.source_path)
    document = build_document(args.source_path, lines, args.max_beat_chars)
    payload = json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":") if args.compact else None,
        indent=None if args.compact else 2,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    if args.check and document["validation"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
