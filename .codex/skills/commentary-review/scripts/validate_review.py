#!/usr/bin/env python3
"""Validate commentary-review inputs and one final review report artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DIMENSIONS = ["accuracy", "consistency", "simplicity", "fun"]
SEVERITIES = ["blocker", "major", "minor"]
FINDING_KEYS = {
    "finding_id", "target_id", "unit_type", "commentary_ref", "related_target_ids",
    "dimension", "severity", "issue", "evidence", "suggestion",
}
PRECHECK_KEYS = {
    "texts_indexed", "form_counts", "max_form_run", "duplicate_pairs",
    "repeated_openings", "length_stats", "term_first_mention",
}
MAX_QUOTE_CHARS = 120


class ValidationFailure(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationFailure(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, where: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{where} must be an object")
    return value


def require_list(value: Any, where: str) -> list[Any]:
    require(isinstance(value, list), f"{where} must be an array")
    return value


def require_text(value: Any, where: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{where} must be non-empty text")
    return value


def require_exact_keys(value: dict[str, Any], keys: set[str], where: str) -> None:
    missing = sorted(keys - set(value))
    extra = sorted(set(value) - keys)
    require(not missing and not extra, f"{where} keys mismatch; missing={missing}, extra={extra}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"Cannot read valid UTF-8 JSON from {path}: {error}")
    return require_dict(value, str(path))


def collect_source(segmentation: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the segmentation into preorder [{id, type, chapter_id, node}]."""
    require(segmentation.get("status") == "ok", "segmentation.status must be 'ok'")
    require_text(segmentation.get("document_id"), "segmentation.document_id")
    require_text(segmentation.get("source_path"), "segmentation.source_path")
    require_text(segmentation.get("source_sha256"), "segmentation.source_sha256")
    book = require_dict(segmentation.get("book"), "segmentation.book")
    sequence: list[dict[str, Any]] = []

    def add(node: dict[str, Any], unit_type: str, chapter_id: str | None) -> None:
        require_text(node.get("id"), f"{unit_type}.id")
        sequence.append({"id": node["id"], "type": unit_type, "chapter_id": chapter_id, "node": node})

    def add_beat(beat: Any, parent_id: str, chapter_id: str) -> None:
        beat = require_dict(beat, f"{parent_id}.beats[]")
        require_text(beat.get("id"), f"{parent_id}.beat.id")
        for key in ("title", "summary", "function", "source_markdown"):
            require(key in beat, f"{beat['id']}: missing source field {key}")
        sequence.append({"id": beat["id"], "type": "beat", "chapter_id": chapter_id, "node": beat})

    add(book, "book", None)
    for chapter in require_list(book.get("chapters"), "book.chapters"):
        chapter = require_dict(chapter, "book.chapters[]")
        for key in ("id", "title", "summary", "function", "flow", "sections"):
            require(key in chapter, f"chapter missing {key}")
        add(chapter, "chapter", chapter["id"])
        for section in require_list(chapter["sections"], f"{chapter['id']}.sections"):
            section = require_dict(section, f"{chapter['id']}.sections[]")
            for key in ("id", "title", "summary", "function", "flow", "subsections", "beats"):
                require(key in section, f"section missing {key}")
            add(section, "section", chapter["id"])
            for beat in require_list(section["beats"], f"{section['id']}.beats"):
                add_beat(beat, section["id"], chapter["id"])
            for subsection in require_list(section["subsections"], f"{section['id']}.subsections"):
                subsection = require_dict(subsection, f"{section['id']}.subsections[]")
                for key in ("id", "title", "summary", "function", "flow", "beats"):
                    require(key in subsection, f"subsection missing {key}")
                add(subsection, "subsection", chapter["id"])
                for beat in require_list(subsection["beats"], f"{subsection['id']}.beats"):
                    add_beat(beat, subsection["id"], chapter["id"])

    ids = [item["id"] for item in sequence]
    require(len(ids) == len(set(ids)), "segmentation IDs must be unique")
    return sequence


def index_commentary(commentary: dict[str, Any], sequence: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Validate the commentary as review input; return target_id -> item record."""
    for key in ("status", "schema_version", "stage", "source", "items"):
        require(key in commentary, f"commentary missing {key}")
    require(commentary["status"] == "ok", "commentary.status must be 'ok'")
    require(commentary["schema_version"] == "0.7.0", "commentary.schema_version must be '0.7.0'")
    require(commentary["stage"] == "book_commentary", "commentary.stage must be 'book_commentary'")
    com_source = require_dict(commentary["source"], "commentary.source")
    seg_root = {"document_id": None}

    by_id = {item["id"]: item for item in sequence}
    items = require_list(commentary["items"], "commentary.items")
    records: dict[str, dict[str, Any]] = {}
    positions: list[int] = []

    for index, item in enumerate(items):
        item = require_dict(item, f"commentary.items[{index}]")
        target_id = require_text(item.get("target_id"), f"commentary.items[{index}].target_id")
        require(target_id in by_id, f"{target_id}: not present in segmentation")
        require(target_id not in records, f"{target_id}: duplicated in commentary items")
        source_item = by_id[target_id]
        unit_type = item.get("unit_type")
        require(unit_type == source_item["type"], f"{target_id}: unit_type mismatch with segmentation")
        texts: list[dict[str, Any]] = []
        if unit_type == "beat":
            for c_index, comment in enumerate(require_list(item.get("commentaries"), f"{target_id}.commentaries")):
                comment = require_dict(comment, f"{target_id}.commentaries[{c_index}]")
                texts.append({
                    "kind": "beat_commentary",
                    "index": c_index,
                    "voice": require_text(comment.get("voice"), f"{target_id}.commentaries[{c_index}].voice"),
                    "text": require_text(comment.get("text"), f"{target_id}.commentaries[{c_index}].text"),
                })
        else:
            body = require_dict(item.get("commentary"), f"{target_id}.commentary")
            opening = require_dict(body.get("opening_hook"), f"{target_id}.commentary.opening_hook")
            closing = require_dict(body.get("closing_question"), f"{target_id}.commentary.closing_question")
            texts.append({"kind": "opening_hook", "index": None, "voice": opening.get("voice"),
                          "text": require_text(opening.get("text"), f"{target_id}.opening_hook.text")})
            texts.append({"kind": "closing_question", "index": None, "voice": closing.get("voice"),
                          "text": require_text(closing.get("text"), f"{target_id}.closing_question.text")})
        records[target_id] = {
            "item_index": index,
            "unit_type": unit_type,
            "chapter_id": source_item["chapter_id"],
            "texts": texts,
        }
        positions.append(sequence.index(source_item))

    require(positions == sorted(positions), "commentary items must follow segmentation preorder")
    beat_ids = [item["id"] for item in sequence if item["type"] == "beat"]
    covered = [target for target in records if records[target]["unit_type"] == "beat"]
    missing_beats = [beat_id for beat_id in beat_ids if beat_id not in records]
    require(not missing_beats, f"commentary missing beats: {missing_beats[:5]}")
    require(len(covered) == len(beat_ids), "commentary beat count mismatch")
    return records


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_quote_targets(record: dict[str, Any]) -> list[str]:
    return [entry["text"] for entry in record["texts"]]


def validate_findings(
    findings: list[Any],
    records: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    last_position = -1
    for index, finding in enumerate(findings):
        where = f"findings[{index}]"
        finding = require_dict(finding, where)
        require_exact_keys(finding, FINDING_KEYS, where)
        expected_id = f"F{index + 1:03d}"
        require(finding["finding_id"] == expected_id, f"{where}: finding_id must be {expected_id}")
        target_id = require_text(finding["target_id"], f"{where}.target_id")
        require(target_id in records, f"{where}: target_id {target_id} not a commentary item")
        record = records[target_id]
        require(finding["unit_type"] == record["unit_type"], f"{where}: unit_type mismatch")
        require(finding["dimension"] in DIMENSIONS, f"{where}: invalid dimension")
        require(finding["severity"] in SEVERITIES, f"{where}: invalid severity")
        require_text(finding["issue"], f"{where}.issue")
        require_text(finding["suggestion"], f"{where}.suggestion")
        require(record["item_index"] >= last_position, f"{where}: findings must follow commentary item order")
        last_position = record["item_index"]

        evidence = require_dict(finding["evidence"], f"{where}.evidence")
        require_exact_keys(evidence, {"commentary_quote", "source_refs"}, f"{where}.evidence")
        quote = require_text(evidence["commentary_quote"], f"{where}.evidence.commentary_quote")
        require(len(quote) <= MAX_QUOTE_CHARS, f"{where}: commentary_quote exceeds {MAX_QUOTE_CHARS} chars")

        ref = finding["commentary_ref"]
        related = finding["related_target_ids"]
        if ref is None:
            require(record["unit_type"] == "chapter", f"{where}: pattern finding must target a chapter item")
            related = require_list(related, f"{where}.related_target_ids")
            require(len(related) >= 2, f"{where}: pattern finding needs >=2 related_target_ids")
            haystacks: list[str] = []
            for related_id in related:
                require(related_id in records, f"{where}: related target {related_id} not a commentary item")
                haystacks.extend(resolve_quote_targets(records[related_id]))
            require(any(quote in text for text in haystacks),
                    f"{where}: commentary_quote not found in any related item's texts")
        else:
            require(related is None, f"{where}: related_target_ids must be null for occurrence findings")
            ref = require_dict(ref, f"{where}.commentary_ref")
            kind = ref.get("kind")
            require(kind in {"opening_hook", "closing_question", "beat_commentary"}, f"{where}: invalid commentary_ref.kind")
            if kind == "beat_commentary":
                require_exact_keys(ref, {"kind", "index", "voice"}, f"{where}.commentary_ref")
                require(record["unit_type"] == "beat", f"{where}: beat_commentary ref on non-beat item")
                entries = [t for t in record["texts"] if t["index"] == ref["index"]]
                require(len(entries) == 1, f"{where}: commentary_ref.index out of range")
                require(entries[0]["voice"] == ref["voice"], f"{where}: commentary_ref.voice mismatch")
                target_text = entries[0]["text"]
            else:
                require_exact_keys(ref, {"kind"}, f"{where}.commentary_ref")
                require(record["unit_type"] != "beat", f"{where}: structural ref on beat item")
                target_text = next(t["text"] for t in record["texts"] if t["kind"] == kind)
            require(quote in target_text, f"{where}: commentary_quote is not a substring of the referenced text")

        source_refs = require_list(evidence["source_refs"], f"{where}.evidence.source_refs")
        has_source_quote = False
        for r_index, source_ref in enumerate(source_refs):
            ref_where = f"{where}.evidence.source_refs[{r_index}]"
            source_ref = require_dict(source_ref, ref_where)
            require_exact_keys(source_ref, {"target_id", "quote_from", "quote"}, ref_where)
            ref_target = require_text(source_ref["target_id"], f"{ref_where}.target_id")
            ref_quote = require_text(source_ref["quote"], f"{ref_where}.quote")
            require(len(ref_quote) <= MAX_QUOTE_CHARS, f"{ref_where}: quote exceeds {MAX_QUOTE_CHARS} chars")
            quote_from = source_ref["quote_from"]
            require(quote_from in {"source", "commentary"}, f"{ref_where}: invalid quote_from")
            if quote_from == "commentary":
                require(ref_target in records, f"{ref_where}: target not a commentary item")
                require(any(ref_quote in text for text in resolve_quote_targets(records[ref_target])),
                        f"{ref_where}: quote not found in {ref_target} commentary texts")
            else:
                require(ref_target in by_id, f"{ref_where}: target not in segmentation")
                node = by_id[ref_target]["node"]
                if by_id[ref_target]["type"] == "beat":
                    haystacks = [node["source_markdown"]]
                else:
                    haystacks = [node.get(key) for key in ("title", "summary", "function", "flow")]
                require(any(isinstance(text, str) and ref_quote in text for text in haystacks),
                        f"{ref_where}: quote not found in {ref_target} source fields")
                has_source_quote = True
        if finding["dimension"] == "accuracy":
            require(has_source_quote, f"{where}: accuracy finding needs >=1 quote_from='source' reference")
        validated.append(finding)
    return validated


def tally(findings: list[dict[str, Any]]):
    by_dimension = {dim: {sev: 0 for sev in SEVERITIES} for dim in DIMENSIONS}
    by_chapter: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {dim: {sev: 0 for sev in SEVERITIES} for dim in DIMENSIONS})
    return by_dimension, by_chapter


def validate_review(review: dict[str, Any], review_path: Path, commentary_path: Path,
                    commentary: dict[str, Any], records: dict[str, dict[str, Any]],
                    sequence: list[dict[str, Any]]) -> int:
    envelope_keys = {"status", "schema_version", "stage", "source", "inputs", "settings",
                     "precheck", "findings", "scores", "summary", "validation"}
    require_exact_keys(review, envelope_keys, "review")
    require(review["status"] == "ok", "review.status must be 'ok'")
    require(review["schema_version"] == "0.7.0", "review.schema_version must be '0.7.0'")
    require(review["stage"] == "commentary_review", "review.stage must be 'commentary_review'")
    require(review["source"] == commentary["source"], "review.source must equal commentary.source")

    inputs = require_dict(review["inputs"], "review.inputs")
    require_exact_keys(inputs, {"segmentation_path", "commentary_path", "commentary_sha256"}, "review.inputs")
    require_text(inputs["segmentation_path"], "review.inputs.segmentation_path")
    require_text(inputs["commentary_path"], "review.inputs.commentary_path")
    require(inputs["commentary_sha256"] == sha256_of(commentary_path),
            "review.inputs.commentary_sha256 does not match the commentary file")

    settings = require_dict(review["settings"], "review.settings")
    require_exact_keys(settings, {"output_language", "reader_profile", "dimensions",
                                  "severity_levels", "score_scale"}, "review.settings")
    require_text(settings["output_language"], "review.settings.output_language")
    require_text(settings["reader_profile"], "review.settings.reader_profile")
    require(settings["dimensions"] == DIMENSIONS, "review.settings.dimensions mismatch")
    require(settings["severity_levels"] == SEVERITIES, "review.settings.severity_levels mismatch")
    require(settings["score_scale"] == "0-10", "review.settings.score_scale must be '0-10'")

    precheck = require_dict(review["precheck"], "review.precheck")
    require_exact_keys(precheck, PRECHECK_KEYS, "review.precheck")

    validation = require_dict(review["validation"], "review.validation")
    require_exact_keys(validation, {"errors", "warnings"}, "review.validation")
    require(validation["errors"] == [], "review.validation.errors must be empty")
    require_list(validation["warnings"], "review.validation.warnings")

    by_id = {item["id"]: item for item in sequence}
    findings = validate_findings(require_list(review["findings"], "review.findings"), records, by_id)

    by_dimension, by_chapter = tally(findings)
    for finding in findings:
        by_dimension[finding["dimension"]][finding["severity"]] += 1
        chapter_id = records[finding["target_id"]]["chapter_id"]
        if chapter_id is not None:
            by_chapter[chapter_id][finding["dimension"]][finding["severity"]] += 1

    scores = require_dict(review["scores"], "review.scores")
    require_exact_keys(scores, {"chapters", "global"}, "review.scores")
    chapter_entries = require_list(scores["chapters"], "review.scores.chapters")
    commentary_chapters = [t for t, r in sorted(records.items(), key=lambda kv: kv[1]["item_index"])
                           if r["unit_type"] == "chapter"]
    require([require_dict(e, "scores.chapters[]").get("chapter_id") for e in chapter_entries] == commentary_chapters,
            "scores.chapters must list every commentary chapter in order")

    weighted: dict[str, float] = {dim: 0.0 for dim in DIMENSIONS}
    total_weight = 0
    for entry in chapter_entries:
        chapter_id = entry["chapter_id"]
        where = f"scores.chapters[{chapter_id}]"
        require_exact_keys(entry, {"chapter_id", "items_reviewed", "dimensions"}, where)
        expected_items = sum(1 for r in records.values() if r["chapter_id"] == chapter_id)
        require(entry["items_reviewed"] == expected_items,
                f"{where}: items_reviewed must be {expected_items}")
        dims = require_dict(entry["dimensions"], f"{where}.dimensions")
        require_exact_keys(dims, set(DIMENSIONS), f"{where}.dimensions")
        for dim in DIMENSIONS:
            cell = require_dict(dims[dim], f"{where}.dimensions.{dim}")
            require_exact_keys(cell, {"score", "blockers", "majors", "minors", "rationale"},
                               f"{where}.dimensions.{dim}")
            score = cell["score"]
            require(isinstance(score, int) and 0 <= score <= 10, f"{where}.{dim}.score must be int 0-10")
            counts = by_chapter[chapter_id][dim]
            for label, sev in (("blockers", "blocker"), ("majors", "major"), ("minors", "minor")):
                require(cell[label] == counts[sev],
                        f"{where}.{dim}.{label} must equal findings tally {counts[sev]}")
            if counts["blocker"]:
                require(score <= 4, f"{where}.{dim}: blocker present, score must be <=4")
            elif counts["major"]:
                require(score <= 7, f"{where}.{dim}: major present, score must be <=7")
            elif counts["minor"]:
                require(score <= 9, f"{where}.{dim}: minor present, score must be <=9")
            else:
                require(score >= 8, f"{where}.{dim}: no findings, score must be >=8")
            require_text(cell["rationale"], f"{where}.{dim}.rationale")
            weighted[dim] += score * entry["items_reviewed"]
        total_weight += entry["items_reviewed"]

    global_scores = require_dict(scores["global"], "review.scores.global")
    require_exact_keys(global_scores, set(DIMENSIONS), "review.scores.global")
    for dim in DIMENSIONS:
        expected = round(weighted[dim] / total_weight, 1) if total_weight else 0.0
        value = global_scores[dim]
        require(isinstance(value, (int, float)) and abs(value - expected) <= 0.05,
                f"review.scores.global.{dim} must be items-weighted mean {expected}")

    summary = require_dict(review["summary"], "review.summary")
    require_exact_keys(summary, {"verdict", "items_reviewed", "items_with_findings",
                                 "by_dimension", "by_severity", "top_issues"}, "review.summary")
    require(summary["items_reviewed"] == len(records), "summary.items_reviewed must equal commentary item count")
    require(summary["items_with_findings"] == len({f["target_id"] for f in findings}),
            "summary.items_with_findings must equal distinct finding targets")
    summary_by_dimension = require_dict(summary["by_dimension"], "summary.by_dimension")
    require_exact_keys(summary_by_dimension, set(DIMENSIONS), "summary.by_dimension")
    for dim in DIMENSIONS:
        cell = require_dict(summary_by_dimension[dim], f"summary.by_dimension.{dim}")
        require_exact_keys(cell, set(SEVERITIES), f"summary.by_dimension.{dim}")
        for sev in SEVERITIES:
            require(cell[sev] == by_dimension[dim][sev], f"summary.by_dimension.{dim}.{sev} tally mismatch")
    by_severity = require_dict(summary["by_severity"], "summary.by_severity")
    require_exact_keys(by_severity, set(SEVERITIES), "summary.by_severity")
    for sev in SEVERITIES:
        expected_count = sum(by_dimension[dim][sev] for dim in DIMENSIONS)
        require(by_severity[sev] == expected_count, f"summary.by_severity.{sev} tally mismatch")
    top_issues = require_list(summary["top_issues"], "summary.top_issues")
    if findings:
        require(1 <= len(top_issues) <= 5, "summary.top_issues must contain 1-5 entries when findings exist")
        for issue in top_issues:
            require_text(issue, "summary.top_issues[]")
    else:
        require(top_issues == [], "summary.top_issues must be empty without findings")
    blockers = sum(by_dimension[dim]["blocker"] for dim in DIMENSIONS)
    majors = sum(by_dimension[dim]["major"] for dim in DIMENSIONS)
    expected_verdict = "rework" if blockers else "revise" if majors else "pass"
    require(summary["verdict"] == expected_verdict, f"summary.verdict must be '{expected_verdict}'")
    return len(findings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("segmentation", type=Path, help="original segmentation JSON")
    parser.add_argument("commentary", type=Path, help="final commentary JSON")
    parser.add_argument("--review", type=Path, help="review report JSON to validate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    segmentation = load_json(args.segmentation)
    commentary = load_json(args.commentary)
    sequence = collect_source(segmentation)
    require(require_dict(commentary.get("source"), "commentary.source").get("source_sha256")
            == segmentation["source_sha256"], "commentary/segmentation source_sha256 mismatch")
    records = index_commentary(commentary, sequence)
    print(f"OK inputs: {len(records)} commentary items over {len(sequence)} source nodes")
    if args.review is None:
        return 0
    review = load_json(args.review)
    finding_count = validate_review(review, args.review, args.commentary, commentary, records, sequence)
    print(f"OK review: {args.review} ({finding_count} findings)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationFailure as error:
        raise SystemExit(f"Validation failed: {error}")
