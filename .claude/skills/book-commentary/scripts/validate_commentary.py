#!/usr/bin/env python3
"""Validate pre-analysis input and one final-only book commentary artifact."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


UNIT_PLAN_KEYS = {
    "primary_goal", "reader_before", "reader_after", "opening_angle",
    "closing_angle", "voice", "presentation_form", "form_rationale",
    "analogy", "reward_design", "tone_tags", "constraints",
}

BEAT_PLAN_KEYS = {
    "mode", "primary_goal", "target_difficulty_labels", "angle",
    "commentary_brief", "loop_contract", "pairing_design", "comment_plans",
}

COMMENT_PLAN_KEYS = {
    "voice", "comment_type", "contribution", "strategy", "roast_move",
    "presentation_form", "form_rationale", "analogy", "delivery_design",
    "tone_tags", "constraints",
}

EXCLUDED_ITEM_KEYS = {
    "summary", "function", "flow", "source_markdown", "conflict",
    "difficulty", "plan", "upstream", "eligibility", "skip_reason",
    "reward_delivery", "contribution", "self_check", "pair_check",
}


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


def collect_source(source: dict[str, Any]):
    require(source.get("status") == "ok", "input.status must be 'ok'")
    require_text(source.get("document_id"), "input.document_id")
    book = require_dict(source.get("book"), "input.book")
    units: list[dict[str, Any]] = []
    beats: list[dict[str, Any]] = []
    sequence: list[dict[str, Any]] = []

    def add_unit(node: dict[str, Any], unit_type: str, chapter_id: str | None) -> None:
        require_text(node.get("id"), f"{unit_type}.id")
        item = {"id": node["id"], "type": unit_type, "chapter_id": chapter_id, "node": node}
        units.append(item)
        sequence.append(item)

    def add_beat(beat: Any, parent_id: str, chapter_id: str) -> None:
        beat = require_dict(beat, f"{parent_id}.beats[]")
        require_text(beat.get("id"), f"{parent_id}.beat.id")
        for key in ("title", "summary", "function", "source_markdown"):
            require(key in beat, f"{beat['id']}: missing source field {key}")
        item = {"id": beat["id"], "type": "beat", "chapter_id": chapter_id, "node": beat}
        beats.append(item)
        sequence.append(item)

    add_unit(book, "book", None)
    for chapter in require_list(book.get("chapters"), "book.chapters"):
        chapter = require_dict(chapter, "book.chapters[]")
        for key in ("id", "title", "summary", "function", "flow", "sections"):
            require(key in chapter, f"chapter missing {key}")
        add_unit(chapter, "chapter", chapter["id"])
        for section in require_list(chapter["sections"], f"{chapter['id']}.sections"):
            section = require_dict(section, f"{chapter['id']}.sections[]")
            for key in ("id", "title", "summary", "function", "flow", "subsections", "beats"):
                require(key in section, f"section missing {key}")
            add_unit(section, "section", chapter["id"])
            for beat in require_list(section["beats"], f"{section['id']}.beats"):
                add_beat(beat, section["id"], chapter["id"])
            for subsection in require_list(section["subsections"], f"{section['id']}.subsections"):
                subsection = require_dict(subsection, f"{section['id']}.subsections[]")
                for key in ("id", "title", "summary", "function", "flow", "beats"):
                    require(key in subsection, f"subsection missing {key}")
                add_unit(subsection, "subsection", chapter["id"])
                for beat in require_list(subsection["beats"], f"{subsection['id']}.beats"):
                    add_beat(beat, subsection["id"], chapter["id"])

    ids = [item["id"] for item in sequence]
    require(len(ids) == len(set(ids)), "source IDs must be unique")
    return units, beats, sequence


def validate_analogy(value: Any, where: str) -> None:
    analogy = require_dict(value, where)
    require_exact_keys(analogy, {"use", "domain", "mapping"}, where)
    require(isinstance(analogy["use"], bool), f"{where}.use must be boolean")
    if analogy["use"]:
        require_text(analogy["domain"], f"{where}.domain")
        require_text(analogy["mapping"], f"{where}.mapping")
    else:
        require(analogy["domain"] is None and analogy["mapping"] is None, f"{where}: unused analogy fields must be null")


def validate_enriched_source(units: list[dict[str, Any]], beats: list[dict[str, Any]]) -> None:
    for item in units:
        node = item["node"]
        where = item["id"]
        require("conflict" in node and "plan" in node, f"{where}: missing conflict or structural plan; run $pre-analysis")
        require((node["conflict"] is None) == (node["plan"] is None), f"{where}: conflict/plan nullability mismatch")
        if node["plan"] is None:
            continue
        conflict = require_dict(node["conflict"], f"{where}.conflict")
        conflict_keys = {"type", "reader_assumption", "counterforce", "stakes", "open_loop", "statement", "evidence_refs", "confidence"}
        require_exact_keys(conflict, conflict_keys, f"{where}.conflict")
        plan = require_dict(node["plan"], f"{where}.plan")
        require_exact_keys(plan, UNIT_PLAN_KEYS, f"{where}.plan")
        require(plan["voice"] in {"mentor", "student"}, f"{where}.plan.voice invalid")
        require_text(plan["presentation_form"], f"{where}.plan.presentation_form")
        validate_analogy(plan["analogy"], f"{where}.plan.analogy")
        constraints = require_dict(plan["constraints"], f"{where}.plan.constraints")
        for key in ("opening_max_chars", "question_max_chars"):
            require(isinstance(constraints.get(key), int) and constraints[key] > 0, f"{where}.plan.constraints.{key} invalid")

    for item in beats:
        beat = item["node"]
        where = item["id"]
        require("difficulty" in beat and "plan" in beat, f"{where}: missing difficulty or beat plan; run $pre-analysis")
        difficulty = require_dict(beat["difficulty"], f"{where}.difficulty")
        require(difficulty.get("level") in {"simple", "medium", "hard"}, f"{where}: invalid difficulty level")
        plan = require_dict(beat["plan"], f"{where}.plan")
        require_exact_keys(plan, BEAT_PLAN_KEYS, f"{where}.plan")
        comment_plans = require_list(plan["comment_plans"], f"{where}.plan.comment_plans")
        require(1 <= len(comment_plans) <= 2, f"{where}: require one or two comment plans")
        voices: list[str] = []
        for index, comment_plan in enumerate(comment_plans):
            comment_plan = require_dict(comment_plan, f"{where}.plan.comment_plans[{index}]")
            require_exact_keys(comment_plan, COMMENT_PLAN_KEYS, f"{where}.plan.comment_plans[{index}]")
            voice = comment_plan["voice"]
            voices.append(voice)
            expected_type = "fun_commentary" if voice == "mentor" else "roast" if voice == "student" else None
            require(comment_plan["comment_type"] == expected_type, f"{where}: voice/type mismatch")
            validate_analogy(comment_plan["analogy"], f"{where}.plan.comment_plans[{index}].analogy")
            constraints = require_dict(comment_plan["constraints"], f"{where}.plan.comment_plans[{index}].constraints")
            require(isinstance(constraints.get("max_chars"), int) and constraints["max_chars"] > 0, f"{where}: max_chars invalid")
        require(voices in (["mentor"], ["student"], ["mentor", "student"]), f"{where}: invalid voice order")


def expected_source_metadata(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": source.get("document_id"),
        "source_path": source.get("source_path"),
        "source_sha256": source.get("source_sha256"),
    }


def validate_envelope(artifact: dict[str, Any], source: dict[str, Any]):
    keys = {"status", "schema_version", "stage", "source", "settings", "items", "validation"}
    require_exact_keys(artifact, keys, "commentary")
    require(artifact["status"] == "ok", "commentary.status must be 'ok'")
    require(artifact["schema_version"] == "0.7.0", "commentary.schema_version must be '0.7.0'")
    require(artifact["stage"] == "book_commentary", "commentary.stage must be 'book_commentary'")
    require(artifact["source"] == expected_source_metadata(source), "commentary.source must match enriched input")
    settings = require_dict(artifact["settings"], "commentary.settings")
    setting_keys = {"output_language", "reader_profile", "unit_voice_policy", "beat_voice_policy", "voice_coverage_target"}
    require_exact_keys(settings, setting_keys, "commentary.settings")
    require_text(settings["output_language"], "commentary.settings.output_language")
    require_text(settings["reader_profile"], "commentary.settings.reader_profile")
    require(settings["unit_voice_policy"] == "select_one", "unit_voice_policy must be select_one")
    require(settings["beat_voice_policy"] == "one_or_both", "beat_voice_policy must be one_or_both")
    coverage = require_dict(settings["voice_coverage_target"], "commentary.settings.voice_coverage_target")
    require_exact_keys(coverage, {"mentor", "student"}, "commentary.settings.voice_coverage_target")
    require(all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in coverage.values()), "coverage targets must be 0..1")
    validation = require_dict(artifact["validation"], "commentary.validation")
    require_exact_keys(validation, {"errors", "warnings"}, "commentary.validation")
    require(validation["errors"] == [], "commentary.validation.errors must be empty")
    require_list(validation["warnings"], "commentary.validation.warnings")
    return require_list(artifact["items"], "commentary.items"), settings


def validate_presentation_text(text: str, form: str, where: str) -> None:
    if form == "arrow_chain":
        require(text.count("→") >= 2, f"{where}: arrow_chain needs at least two arrows")
    if form == "bullet_breakdown":
        bullets = [line for line in text.splitlines() if line.lstrip().startswith(("- ", "* ", "• "))]
        require(len(bullets) >= 2, f"{where}: bullet_breakdown needs at least two bullets")


def find_excluded_key(value: Any, path: str = "items") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in EXCLUDED_ITEM_KEYS:
                return f"{path}.{key}"
            found = find_excluded_key(child, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = find_excluded_key(child, f"{path}[{index}]")
            if found:
                return found
    return None


def validate_commentary_items(items: list[Any], sequence: list[dict[str, Any]], settings: dict[str, Any]) -> None:
    expected = [item for item in sequence if item["type"] == "beat" or item["node"]["plan"] is not None]
    records = [require_dict(item, f"items[{index}]") for index, item in enumerate(items)]
    require([record.get("target_id") for record in records] == [item["id"] for item in expected], "item IDs/order differ from source preorder")
    excluded = find_excluded_key(records)
    require(excluded is None, f"final commentary contains excluded key: {excluded}")
    chapter_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"mentor": 0, "student": 0, "total": 0})

    for record, source_item in zip(records, expected):
        target_id = source_item["id"]
        if source_item["type"] != "beat":
            require_exact_keys(record, {"target_id", "unit_type", "commentary"}, target_id)
            require(record["unit_type"] == source_item["type"], f"{target_id}: unit_type mismatch")
            plan = source_item["node"]["plan"]
            commentary = require_dict(record["commentary"], f"{target_id}.commentary")
            require_exact_keys(commentary, {"opening_hook", "closing_question"}, f"{target_id}.commentary")
            opening = require_dict(commentary["opening_hook"], f"{target_id}.commentary.opening_hook")
            require_exact_keys(opening, {"voice", "presentation_form", "text"}, f"{target_id}.commentary.opening_hook")
            opening_text = require_text(opening["text"], f"{target_id}.commentary.opening_hook.text")
            require(opening["voice"] == plan["voice"], f"{target_id}: opening voice differs from plan")
            require(opening["presentation_form"] == plan["presentation_form"], f"{target_id}: opening form differs from plan")
            require(len(opening_text) <= plan["constraints"]["opening_max_chars"], f"{target_id}: opening exceeds max_chars")
            validate_presentation_text(opening_text, opening["presentation_form"], f"{target_id}.opening_hook")
            closing = require_dict(commentary["closing_question"], f"{target_id}.commentary.closing_question")
            require_exact_keys(closing, {"voice", "text", "answerability"}, f"{target_id}.commentary.closing_question")
            closing_text = require_text(closing["text"], f"{target_id}.commentary.closing_question.text")
            require(closing["voice"] == plan["voice"], f"{target_id}: closing voice differs from plan")
            require(closing["answerability"] in {"within_unit", "reflection", "forward_bridge"}, f"{target_id}: invalid answerability")
            require(len(closing_text) <= plan["constraints"]["question_max_chars"], f"{target_id}: question exceeds max_chars")
            continue

        require_exact_keys(record, {"target_id", "unit_type", "commentaries"}, target_id)
        require(record["unit_type"] == "beat", f"{target_id}: unit_type must be beat")
        planned = source_item["node"]["plan"]["comment_plans"]
        comments = require_list(record["commentaries"], f"{target_id}.commentaries")
        require(len(comments) == len(planned), f"{target_id}: commentary count differs from plan")
        voices: list[str] = []
        for index, (comment, comment_plan) in enumerate(zip(comments, planned)):
            comment = require_dict(comment, f"{target_id}.commentaries[{index}]")
            require_exact_keys(comment, {"voice", "comment_type", "presentation_form", "text"}, f"{target_id}.commentaries[{index}]")
            for key in ("voice", "comment_type", "presentation_form"):
                require(comment[key] == comment_plan[key], f"{target_id}.commentaries[{index}].{key} differs from plan")
            text = require_text(comment["text"], f"{target_id}.commentaries[{index}].text")
            require(len(text) <= comment_plan["constraints"]["max_chars"], f"{target_id}.commentaries[{index}] exceeds max_chars")
            validate_presentation_text(text, comment["presentation_form"], f"{target_id}.commentaries[{index}]")
            voices.append(comment["voice"])
        counts = chapter_counts[source_item["chapter_id"]]
        counts["total"] += 1
        for voice in set(voices):
            counts[voice] += 1

    targets = settings["voice_coverage_target"]
    for chapter_id, counts in chapter_counts.items():
        for voice in ("mentor", "student"):
            actual = counts[voice] / counts["total"] if counts["total"] else 0
            require(actual + 1e-12 >= targets[voice], f"{chapter_id}: {voice} coverage {actual:.3f} below {targets[voice]:.3f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="pre-analysis enriched segmentation JSON")
    parser.add_argument("--commentary", type=Path, help="single final commentary JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = load_json(args.source)
    units, beats, sequence = collect_source(source)
    validate_enriched_source(units, beats)
    print(f"OK enriched input: {len(units)} structural nodes, {len(beats)} beats")
    if args.commentary is None:
        return 0
    artifact = load_json(args.commentary)
    items, settings = validate_envelope(artifact, source)
    validate_commentary_items(items, sequence, settings)
    print(f"OK commentary: {args.commentary} ({len(items)} final-comment items)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationFailure as error:
        raise SystemExit(f"Validation failed: {error}")
