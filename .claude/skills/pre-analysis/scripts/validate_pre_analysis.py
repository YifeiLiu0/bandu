#!/usr/bin/env python3
"""Validate an enriched pre-analysis JSON against its untouched source."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


CONFLICT_TYPES = {
    "expectation_vs_reality", "goal_vs_obstacle", "intuition_vs_mechanism",
    "old_model_vs_new_model", "simplicity_vs_reliability", "benefit_vs_cost",
    "question_vs_missing_answer",
}
EMOTIONS = {"surprise", "relief", "control", "curiosity", "vigilance"}
VOICES = {"mentor", "student"}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def structural_nodes(data: dict[str, Any]):
    book = data["book"]
    yield book
    for chapter in book["chapters"]:
        yield chapter
        for section in chapter["sections"]:
            yield section
            for subsection in section.get("subsections", []):
                yield subsection


def beat_nodes(data: dict[str, Any]):
    for chapter in data["book"]["chapters"]:
        for section in chapter["sections"]:
            yield from section.get("beats", [])
            for subsection in section.get("subsections", []):
                yield from subsection.get("beats", [])


def strip_analysis(data: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(data)
    for node in structural_nodes(result):
        node.pop("conflict", None)
        node.pop("plan", None)
    for beat in beat_nodes(result):
        beat.pop("difficulty", None)
        beat.pop("plan", None)
    return result


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_conflict(node: dict[str, Any]) -> None:
    value = node["conflict"]
    if value is None:
        return
    required = {"type", "reader_assumption", "counterforce", "stakes", "open_loop", "statement", "evidence_refs", "confidence"}
    require(set(value) == required, f"{node['id']}.conflict keys do not match contract")
    require(value["type"] in CONFLICT_TYPES, f"{node['id']}: invalid conflict type")
    for key in ("reader_assumption", "counterforce", "stakes", "open_loop", "statement"):
        require(nonempty(value[key]), f"{node['id']}.conflict.{key} must be non-empty")
    require(isinstance(value["evidence_refs"], list) and value["evidence_refs"], f"{node['id']}: conflict evidence required")
    require(value["confidence"] in {"low", "medium", "high"}, f"{node['id']}: invalid confidence")


def validate_unit_plan(node: dict[str, Any]) -> None:
    plan = node["plan"]
    require((node["conflict"] is None) == (plan is None), f"{node['id']}: conflict/plan nullability mismatch")
    if plan is None:
        return
    required = {"primary_goal", "reader_before", "reader_after", "opening_angle", "closing_angle", "voice", "presentation_form", "form_rationale", "analogy", "reward_design", "tone_tags", "constraints"}
    require(set(plan) == required, f"{node['id']}.plan keys do not match structural contract")
    require(plan["voice"] in VOICES, f"{node['id']}: invalid structural voice")
    require(nonempty(plan["form_rationale"]), f"{node['id']}: form rationale required")
    reward = plan["reward_design"]
    require(reward.get("emotional_target") in EMOTIONS, f"{node['id']}: invalid emotional target")
    require(nonempty(reward.get("promised_payoff")), f"{node['id']}: promised payoff required")


def validate_difficulty(beat: dict[str, Any]) -> None:
    value = beat["difficulty"]
    required = {"dimensions", "score", "level", "rationale", "difficulty_points", "interest_seed"}
    require(isinstance(value, dict) and set(value) == required, f"{beat['id']}.difficulty keys do not match contract")
    dimensions = value["dimensions"]
    dimension_keys = {"abstraction", "prerequisite_load", "reasoning_gap", "terminology_density", "representation_complexity"}
    require(set(dimensions) == dimension_keys, f"{beat['id']}: difficulty dimensions mismatch")
    require(all(isinstance(score, int) and 0 <= score <= 2 for score in dimensions.values()), f"{beat['id']}: dimension out of range")
    score = sum(dimensions.values())
    require(value["score"] == score, f"{beat['id']}: difficulty score mismatch")
    expected_level = "simple" if score <= 3 else "medium" if score <= 6 else "hard"
    require(value["level"] == expected_level, f"{beat['id']}: difficulty level mismatch")
    require(nonempty(value["rationale"]) and nonempty(value["interest_seed"]), f"{beat['id']}: rationale and interest seed required")
    points = value["difficulty_points"]
    require(isinstance(points, list), f"{beat['id']}: difficulty_points must be an array")
    labels = set()
    for point in points:
        require(set(point) == {"label", "reader_friction", "evidence"}, f"{beat['id']}: invalid difficulty point")
        require(nonempty(point["label"]) and point["label"] not in labels, f"{beat['id']}: duplicate or empty difficulty label")
        require(nonempty(point["reader_friction"]) and nonempty(point["evidence"]), f"{beat['id']}: incomplete difficulty point")
        labels.add(point["label"])


def validate_beat_plan(beat: dict[str, Any]) -> None:
    plan = beat["plan"]
    required = {"mode", "primary_goal", "target_difficulty_labels", "angle", "commentary_brief", "loop_contract", "pairing_design", "comment_plans"}
    require(isinstance(plan, dict) and set(plan) == required, f"{beat['id']}.plan keys do not match beat contract")
    expected_mode = "fun_brief" if beat["difficulty"]["level"] == "simple" else "fun_explanation"
    require(plan["mode"] == expected_mode, f"{beat['id']}: mode contradicts difficulty")
    available_labels = {point["label"] for point in beat["difficulty"]["difficulty_points"]}
    target_labels = plan["target_difficulty_labels"]
    require(isinstance(target_labels, list) and len(target_labels) == len(set(target_labels)), f"{beat['id']}: duplicate difficulty targets")
    require(set(target_labels) <= available_labels, f"{beat['id']}: plan targets unknown difficulty labels")
    brief = plan["commentary_brief"]
    for key in ("reader_old_belief", "central_question", "tension", "information_turn"):
        require(nonempty(brief.get(key)), f"{beat['id']}.commentary_brief.{key} required")
    require(brief.get("emotional_target") in EMOTIONS, f"{beat['id']}: invalid beat emotional target")
    comments = plan["comment_plans"]
    require(isinstance(comments, list) and 1 <= len(comments) <= 2, f"{beat['id']}: one or two comment plans required")
    voices = [comment.get("voice") for comment in comments]
    require(voices in (["mentor"], ["student"], ["mentor", "student"]), f"{beat['id']}: invalid voice order")
    require((len(comments) == 2) == (plan["pairing_design"] is not None), f"{beat['id']}: pairing design mismatch")
    loop = plan["loop_contract"]
    require(loop.get("action") in {"close", "close_and_open"}, f"{beat['id']}: invalid loop action")
    if loop["action"] == "close_and_open":
        require("mentor" in voices, f"{beat['id']}: opened loop requires mentor")
        require(brief.get("next_dependency") is not None, f"{beat['id']}: opened loop needs dependency")
    else:
        require(brief.get("next_dependency") is None, f"{beat['id']}: closed loop cannot have dependency")
    for comment in comments:
        voice = comment["voice"]
        expected_type = "fun_commentary" if voice == "mentor" else "roast"
        require(comment.get("comment_type") == expected_type, f"{beat['id']}: voice/type mismatch")
        require(isinstance(comment.get("constraints", {}).get("max_chars"), int), f"{beat['id']}: max_chars required")


def validate_order(node: dict[str, Any], through: int, structural: bool) -> None:
    keys = list(node)
    if structural:
        if through >= 1:
            require("conflict" in node, f"{node['id']}: missing conflict")
            anchor = "flow" if "flow" in node else "title" if "title" in node else "id"
            require(keys.index("conflict") == keys.index(anchor) + 1, f"{node['id']}: conflict misplaced")
        if through >= 2:
            require("plan" in node, f"{node['id']}: missing structural plan")
            require(keys.index("plan") == keys.index("conflict") + 1, f"{node['id']}: structural plan misplaced")
    else:
        if through >= 3:
            require("difficulty" in node, f"{node['id']}: missing difficulty")
            require(keys.index("difficulty") == keys.index("function") + 1, f"{node['id']}: difficulty misplaced")
        if through >= 4:
            require("plan" in node, f"{node['id']}: missing beat plan")
            require(keys.index("plan") == keys.index("difficulty") + 1, f"{node['id']}: beat plan misplaced")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("enriched", type=Path)
    parser.add_argument("--through", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    original = json.loads(args.original.read_bytes().decode("utf-8"))
    enriched = json.loads(args.enriched.read_bytes().decode("utf-8"))
    require(strip_analysis(enriched) == original, "Existing source content or hierarchy changed")

    structures = list(structural_nodes(enriched))
    beats = list(beat_nodes(enriched))
    for node in structures:
        validate_order(node, args.through, True)
        if args.through >= 1:
            validate_conflict(node)
        if args.through >= 2:
            validate_unit_plan(node)
    for beat in beats:
        validate_order(beat, args.through, False)
        if args.through >= 3:
            validate_difficulty(beat)
        if args.through >= 4:
            validate_beat_plan(beat)
    print(f"Validation passed through stage {args.through}: {len(structures)} structural nodes, {len(beats)} beats")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        raise SystemExit(f"Validation failed: {error}")
