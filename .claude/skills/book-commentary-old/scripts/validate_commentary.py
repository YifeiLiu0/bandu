#!/usr/bin/env python3
"""Validate segmented-book input and staged book-commentary JSON artifacts."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


STAGES = [
    ("01-unit-conflicts.json", "unit_conflicts", "unit"),
    ("02-unit-plans.json", "unit_plans", "unit"),
    ("03-unit-comments.json", "unit_comments", "unit"),
    ("04-beat-difficulties.json", "beat_difficulties", "beat"),
    ("05-beat-plans.json", "beat_plans", "beat"),
    ("06-beat-comments.json", "beat_comments", "beat"),
]
DIMENSIONS = (
    "abstraction",
    "prerequisite_load",
    "reasoning_gap",
    "terminology_density",
    "representation_complexity",
)
VOICES = {"mentor", "student"}
ANSWERABILITY = {"within_unit", "reflection", "forward_bridge"}
SCHEMA_VERSIONS = {
    "0.1.0",
    "0.2.0",
    "0.3.0",
    "0.4.0",
    "0.5.0",
    "0.6.0",
    "0.7.0",
}
PRESENTATION_FORMS = {
    "short_paragraph",
    "core_question",
    "arrow_chain",
    "bullet_breakdown",
    "contrast_pair",
    "mini_dialogue",
    "scene_then_point",
}
THIRD_STAGE_CHECKS = (
    "analysis_aligned",
    "beginner_clear",
    "engaging",
    "narrative_momentum",
)
V04_READABILITY_CHECKS = (
    "readable_rhythm",
    "format_fit",
    "colloquial_and_concrete",
)
PAYOFF_TYPES = {
    "understanding",
    "judgment",
    "action",
    "misconception_correction",
    "connection",
}
EMOTIONAL_TARGETS = {"surprise", "relief", "control", "curiosity", "vigilance"}
ENTRY_FUNCTIONS = {
    "misconception",
    "stakes",
    "mystery",
    "conflict",
    "personal_relevance",
}
EXPLANATION_FUNCTIONS = {
    "analogy",
    "personification",
    "mini_scene",
    "counterexample",
    "contrast",
    "missing_prerequisite",
    "author_intent",
    "source_trace",
}
EXIT_FUNCTIONS = {
    "payoff",
    "mental_model",
    "chapter_position",
    "bridge",
    "memory_anchor",
}
LOOP_ACTIONS = {"close", "close_and_open"}
LIVELY_TURN_DEVICES = {
    "micro_scene",
    "inner_monologue",
    "role_dialogue",
    "consequence_zoom",
    "plainspoken_reframe",
    "none",
}
ROAST_MOVES = {
    "promise_vs_reality",
    "literal_consequence",
    "role_personification",
    "everyday_mapping",
    "deadpan_relabeling",
    "dialogue_snap",
}
FUN_EXPLANATION_STRATEGIES = {
    "concrete_analogy",
    "micro_scenario",
    "step_by_step_bridge",
    "contrast_pair",
    "misconception_correction",
    "plain_language_reframe",
}
FUN_BRIEF_STRATEGIES = {
    "light_observation",
    "useful_connection",
    "reader_reaction",
    "small_surprise",
    "gentle_wit",
}
FUTURE_EVIDENCE_FIELDS = {"title", "summary", "function"}
V05_UNIT_CHECKS = (
    "hook_promise_specific",
    "payoff_checkpoint_grounded",
    "healthy_continuation",
)
V05_REWARD_CHECKS = (
    "payoff_delivered",
    "competence_restored",
    "bridge_grounded",
    "no_fake_cliffhanger",
    "one_cognitive_job",
)
V06_UNIT_STYLE_CHECKS = (
    "companion_voice",
    "lecture_scaffolding_removed",
)
V06_BEAT_STYLE_CHECKS = (
    "companion_voice",
    "lecture_scaffolding_removed",
    "human_entry_realized",
)
V07_STUDENT_CHECKS = (
    "student_roast_fulfilled",
    "first_person_not_crutch",
)


class ValidationFailure(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationFailure(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationFailure(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationFailure(f"root must be an object: {path}")
    return value


def require(obj: dict[str, Any], key: str, where: str, expected: type | None = None) -> Any:
    if key not in obj:
        raise ValidationFailure(f"{where}: missing {key}")
    value = obj[key]
    if expected is not None and not isinstance(value, expected):
        raise ValidationFailure(f"{where}.{key}: expected {expected.__name__}")
    return value


def require_text(obj: dict[str, Any], key: str, where: str) -> str:
    value = require(obj, key, where, str)
    if not value.strip():
        raise ValidationFailure(f"{where}.{key}: must not be empty")
    return value


def validate_delivery_plan(plan: dict[str, Any], where: str) -> bool:
    presentation_form = require_text(plan, "presentation_form", where)
    if presentation_form not in PRESENTATION_FORMS:
        raise ValidationFailure(f"{where}: invalid presentation_form")

    analogy = require(plan, "analogy", where, dict)
    use = analogy.get("use")
    if type(use) is not bool:
        raise ValidationFailure(f"{where}.analogy.use must be a boolean")
    if use:
        require_text(analogy, "domain", f"{where}.analogy")
        require_text(analogy, "mapping", f"{where}.analogy")
    elif analogy.get("domain") is not None or analogy.get("mapping") is not None:
        raise ValidationFailure(
            f"{where}.analogy domain and mapping must be null when use is false"
        )
    return use


def validate_presentation_text(text: str, presentation_form: str, where: str) -> None:
    if presentation_form == "arrow_chain" and text.count("→") < 2:
        raise ValidationFailure(f"{where}: arrow_chain needs at least three nodes")
    if presentation_form == "bullet_breakdown":
        bullet_lines = [
            line
            for line in text.splitlines()
            if line.lstrip().startswith(("- ", "* ", "• "))
        ]
        if len(bullet_lines) < 2:
            raise ValidationFailure(f"{where}: bullet_breakdown needs at least two bullets")
    if presentation_form == "core_question" and not ({"?", "？"} & set(text)):
        raise ValidationFailure(f"{where}: core_question needs an explicit question")


def validate_v04_checks(
    checks: dict[str, Any], analogy_used: bool, where: str
) -> None:
    for key in V04_READABILITY_CHECKS:
        if checks.get(key) is not True:
            raise ValidationFailure(f"{where}.{key} must be true")
    analogy_mapped = checks.get("analogy_mapped")
    if analogy_used and analogy_mapped is not True:
        raise ValidationFailure(f"{where}.analogy_mapped must be true")
    if not analogy_used and analogy_mapped is not None:
        raise ValidationFailure(f"{where}.analogy_mapped must be null")


def validate_enum(value: Any, allowed: set[str], where: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValidationFailure(f"{where} must be one of: {choices}")
    return value


def validate_optional_enum(value: Any, allowed: set[str], where: str) -> str | None:
    if value is None:
        return None
    return validate_enum(value, allowed, where)


def validate_evidence_refs(
    refs: Any,
    target_id: str,
    where: str,
    *,
    require_nonempty: bool,
) -> list[dict[str, Any]]:
    if not isinstance(refs, list):
        raise ValidationFailure(f"{where}: expected list")
    if require_nonempty and not refs:
        raise ValidationFailure(f"{where}: must not be empty")
    for index, ref in enumerate(refs):
        ref_where = f"{where}[{index}]"
        if not isinstance(ref, dict):
            raise ValidationFailure(f"{ref_where}: expected object")
        if ref.get("node_id") != target_id:
            raise ValidationFailure(f"{ref_where}.node_id must be {target_id}")
        field = ref.get("field")
        if field not in FUTURE_EVIDENCE_FIELDS:
            allowed = ", ".join(sorted(FUTURE_EVIDENCE_FIELDS))
            raise ValidationFailure(f"{ref_where}.field must be one of: {allowed}")
    return refs


def validate_function_tags(tags: dict[str, Any], where: str) -> None:
    for key in ("entry", "explanation", "exit"):
        if key not in tags:
            raise ValidationFailure(f"{where}: missing {key}")
    validate_optional_enum(tags.get("entry"), ENTRY_FUNCTIONS, f"{where}.entry")
    validate_optional_enum(
        tags.get("explanation"), EXPLANATION_FUNCTIONS, f"{where}.explanation"
    )
    validate_enum(tags.get("exit"), EXIT_FUNCTIONS, f"{where}.exit")


def validate_v05_unit_reward_design(
    plan: dict[str, Any], allowed_checkpoints: list[str], where: str
) -> dict[str, Any]:
    reward = require(plan, "reward_design", where, dict)
    validate_enum(
        reward.get("hook_function"),
        ENTRY_FUNCTIONS,
        f"{where}.reward_design.hook_function",
    )
    require_text(reward, "promised_payoff", f"{where}.reward_design")
    checkpoint = require_text(reward, "payoff_checkpoint_id", f"{where}.reward_design")
    if checkpoint not in allowed_checkpoints:
        allowed = ", ".join(allowed_checkpoints) or "<none>"
        raise ValidationFailure(
            f"{where}.reward_design.payoff_checkpoint_id must be one of: {allowed}"
        )
    validate_enum(
        reward.get("emotional_target"),
        EMOTIONAL_TARGETS,
        f"{where}.reward_design.emotional_target",
    )
    validate_enum(
        reward.get("closing_function"),
        EXIT_FUNCTIONS,
        f"{where}.reward_design.closing_function",
    )
    return reward


def validate_v05_checks(checks: dict[str, Any], keys: tuple[str, ...], where: str) -> None:
    for key in keys:
        if checks.get(key) is not True:
            raise ValidationFailure(f"{where}.{key} must be true")


def validate_source(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if source.get("status") != "ok":
        raise ValidationFailure("input.status must be 'ok'")
    require_text(source, "document_id", "input")
    book = require(source, "book", "input", dict)
    require_text(book, "id", "book")
    chapters = require(book, "chapters", "book", list)

    units: list[dict[str, Any]] = [{"id": book["id"], "type": "book", "node": book}]
    beats: list[dict[str, Any]] = []
    seen: set[str] = {book["id"]}

    def register(node: dict[str, Any], node_type: str, parent_id: str) -> None:
        node_id = require_text(node, "id", node_type)
        if node_id in seen:
            raise ValidationFailure(f"duplicate node id: {node_id}")
        seen.add(node_id)
        if node_type == "beat":
            for field in ("title", "summary", "function", "source_markdown"):
                require_text(node, field, node_id)
            beats.append({"id": node_id, "type": node_type, "parent_id": parent_id, "node": node})
        else:
            for field in ("title", "summary", "function", "flow"):
                require_text(node, field, node_id)
            units.append({"id": node_id, "type": node_type, "parent_id": parent_id, "node": node})

    for chapter in chapters:
        if not isinstance(chapter, dict):
            raise ValidationFailure("book.chapters items must be objects")
        register(chapter, "chapter", book["id"])
        for section in require(chapter, "sections", chapter["id"], list):
            if not isinstance(section, dict):
                raise ValidationFailure(f"{chapter['id']}.sections items must be objects")
            register(section, "section", chapter["id"])
            section_beats = require(section, "beats", section["id"], list)
            subsections = require(section, "subsections", section["id"], list)
            for beat in section_beats:
                if not isinstance(beat, dict):
                    raise ValidationFailure(f"{section['id']}.beats items must be objects")
                register(beat, "beat", section["id"])
            for subsection in subsections:
                if not isinstance(subsection, dict):
                    raise ValidationFailure(f"{section['id']}.subsections items must be objects")
                register(subsection, "subsection", section["id"])
                for beat in require(subsection, "beats", subsection["id"], list):
                    if not isinstance(beat, dict):
                        raise ValidationFailure(f"{subsection['id']}.beats items must be objects")
                    register(beat, "beat", subsection["id"])

    return units, beats


def build_unit_child_ids(units: list[dict[str, Any]]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for unit in units:
        node = unit["node"]
        unit_type = unit["type"]
        if unit_type == "book":
            child_nodes = node["chapters"]
        elif unit_type == "chapter":
            child_nodes = node["sections"]
        elif unit_type == "section":
            child_nodes = [*node["beats"], *node["subsections"]]
        else:
            child_nodes = node["beats"]
        children[unit["id"]] = [child["id"] for child in child_nodes]
    return children


def build_beat_neighbors(beats: list[dict[str, Any]]) -> dict[str, dict[str, str | None]]:
    sibling_groups: dict[str, list[str]] = {}
    for beat in beats:
        sibling_groups.setdefault(beat["parent_id"], []).append(beat["id"])

    neighbors: dict[str, dict[str, str | None]] = {}
    for sibling_ids in sibling_groups.values():
        for index, target_id in enumerate(sibling_ids):
            neighbors[target_id] = {
                "previous_id": sibling_ids[index - 1] if index > 0 else None,
                "next_id": sibling_ids[index + 1] if index + 1 < len(sibling_ids) else None,
                "second_next_id": (
                    sibling_ids[index + 2] if index + 2 < len(sibling_ids) else None
                ),
            }
    return neighbors


def expected_level(score: int) -> str:
    if score <= 3:
        return "simple"
    if score <= 6:
        return "medium"
    return "hard"


def validate_envelope(
    artifact: dict[str, Any],
    stage_name: str,
    source: dict[str, Any],
    expected_ids: list[str],
    path: Path,
) -> dict[str, dict[str, Any]]:
    where = path.name
    if artifact.get("status") != "ok":
        raise ValidationFailure(f"{where}.status must be 'ok'")
    if artifact.get("schema_version") not in SCHEMA_VERSIONS:
        allowed = ", ".join(sorted(SCHEMA_VERSIONS))
        raise ValidationFailure(f"{where}.schema_version must be one of: {allowed}")
    if artifact.get("stage") != stage_name:
        raise ValidationFailure(f"{where}.stage must be {stage_name!r}")
    source_meta = require(artifact, "source", where, dict)
    if source_meta.get("document_id") != source.get("document_id"):
        raise ValidationFailure(f"{where}: source document_id mismatch")
    input_sha = source.get("source_sha256")
    if input_sha is not None and source_meta.get("source_sha256") != input_sha:
        raise ValidationFailure(f"{where}: source_sha256 mismatch")
    settings = require(artifact, "settings", where, dict)
    require_text(settings, "output_language", f"{where}.settings")
    require_text(settings, "reader_profile", f"{where}.settings")
    if artifact.get("schema_version") == "0.7.0":
        if settings.get("unit_voice_policy") != "select_one":
            raise ValidationFailure(
                f"{where}.settings.unit_voice_policy must be 'select_one'"
            )
        if settings.get("beat_voice_policy") != "one_or_both":
            raise ValidationFailure(
                f"{where}.settings.beat_voice_policy must be 'one_or_both'"
            )
        coverage = require(
            settings, "voice_coverage_target", f"{where}.settings", dict
        )
        for voice in ("mentor", "student"):
            target = coverage.get(voice)
            if (
                isinstance(target, bool)
                or not isinstance(target, (int, float))
                or not 0.7 <= target <= 1.0
            ):
                raise ValidationFailure(
                    f"{where}.settings.voice_coverage_target.{voice} "
                    "must be a number from 0.7 through 1.0"
                )
    elif settings.get("voice_policy") != "select_one":
        raise ValidationFailure(f"{where}.settings.voice_policy must be 'select_one'")
    items = require(artifact, "items", where, list)
    validation = require(artifact, "validation", where, dict)
    if validation.get("errors") != []:
        raise ValidationFailure(f"{where}.validation.errors must be []")

    actual_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationFailure(f"{where}.items[{index}] must be an object")
        target_id = require_text(item, "target_id", f"{where}.items[{index}]")
        if target_id in by_id:
            raise ValidationFailure(f"{where}: duplicate target_id {target_id}")
        actual_ids.append(target_id)
        by_id[target_id] = item
    if actual_ids != expected_ids:
        raise ValidationFailure(
            f"{where}: target IDs/order mismatch; expected {len(expected_ids)}, got {len(actual_ids)}"
        )
    return by_id


def validate_unit_conflicts(items: dict[str, dict[str, Any]]) -> None:
    for target_id, item in items.items():
        eligibility = item.get("eligibility")
        if eligibility not in {"generate", "provisional", "skip"}:
            raise ValidationFailure(f"{target_id}: invalid eligibility")
        require_text(item, "unit_type", target_id)
        if eligibility == "skip":
            if item.get("conflict") is not None:
                raise ValidationFailure(f"{target_id}: skipped conflict must be null")
            require_text(item, "skip_reason", target_id)
            continue
        conflict = require(item, "conflict", target_id, dict)
        for field in (
            "type",
            "reader_assumption",
            "counterforce",
            "stakes",
            "open_loop",
            "statement",
            "confidence",
        ):
            require_text(conflict, field, f"{target_id}.conflict")
        evidence = require(conflict, "evidence_refs", f"{target_id}.conflict", list)
        if not evidence:
            raise ValidationFailure(f"{target_id}: conflict needs evidence_refs")
        if eligibility == "provisional":
            if item.get("context_quality") != "partial":
                raise ValidationFailure(f"{target_id}: provisional context must be partial")
            missing = require(item, "missing_fields", target_id, list)
            if not missing:
                raise ValidationFailure(f"{target_id}: provisional record needs missing_fields")


def validate_unit_plans(
    items: dict[str, dict[str, Any]],
    upstream: dict[str, dict[str, Any]],
    require_v04_delivery: bool,
    require_v05_reward: bool,
    require_v06_plan: bool,
    allowed_checkpoints: dict[str, list[str]],
) -> None:
    for target_id, item in items.items():
        eligibility = item.get("eligibility")
        if eligibility != upstream[target_id].get("eligibility"):
            raise ValidationFailure(f"{target_id}: eligibility differs from stage 1")
        if eligibility == "skip":
            if item.get("plan") is not None:
                raise ValidationFailure(f"{target_id}: skipped plan must be null")
            require_text(item, "skip_reason", target_id)
            continue
        plan = require(item, "plan", target_id, dict)
        for field in (
            "primary_goal",
            "reader_before",
            "reader_after",
            "opening_angle",
            "closing_angle",
            "voice",
        ):
            require_text(plan, field, f"{target_id}.plan")
        if plan["voice"] not in VOICES:
            raise ValidationFailure(f"{target_id}: invalid plan voice")
        if require_v04_delivery:
            validate_delivery_plan(plan, f"{target_id}.plan")
        if require_v06_plan:
            require_text(plan, "form_rationale", f"{target_id}.plan")
        if require_v05_reward:
            validate_v05_unit_reward_design(
                plan,
                allowed_checkpoints[target_id],
                f"{target_id}.plan",
            )
        tone_tags = require(plan, "tone_tags", f"{target_id}.plan", list)
        if not tone_tags:
            raise ValidationFailure(f"{target_id}: tone_tags must not be empty")
        constraints = require(plan, "constraints", f"{target_id}.plan", dict)
        require(constraints, "must", f"{target_id}.plan.constraints", list)
        require(constraints, "avoid", f"{target_id}.plan.constraints", list)
        require_text(constraints, "spoiler_boundary", f"{target_id}.plan.constraints")
        for key in ("opening_max_chars", "question_max_chars"):
            value = constraints.get(key)
            if type(value) is not int or value <= 0:
                raise ValidationFailure(f"{target_id}: {key} must be a positive integer")


def validate_unit_comments(
    items: dict[str, dict[str, Any]],
    plans: dict[str, dict[str, Any]],
    require_third_stage_checks: bool,
    require_v04_delivery: bool,
    require_v05_reward: bool,
    require_v06_style: bool,
) -> None:
    for target_id, item in items.items():
        eligibility = item.get("eligibility")
        if eligibility != plans[target_id].get("eligibility"):
            raise ValidationFailure(f"{target_id}: eligibility differs from stage 2")
        if eligibility == "skip":
            if item.get("commentary") is not None:
                raise ValidationFailure(f"{target_id}: skipped commentary must be null")
            continue
        commentary = require(item, "commentary", target_id, dict)
        hook = require(commentary, "opening_hook", f"{target_id}.commentary", dict)
        question = require(commentary, "closing_question", f"{target_id}.commentary", dict)
        hook_text = require_text(hook, "text", f"{target_id}.opening_hook")
        require_text(question, "text", f"{target_id}.closing_question")
        if question.get("answerability") not in ANSWERABILITY:
            raise ValidationFailure(f"{target_id}: invalid answerability")
        planned_voice = plans[target_id]["plan"]["voice"]
        if hook.get("voice") != planned_voice or question.get("voice") != planned_voice:
            raise ValidationFailure(f"{target_id}: commentary voice differs from plan")
        if require_v04_delivery:
            planned_form = plans[target_id]["plan"]["presentation_form"]
            if hook.get("presentation_form") != planned_form:
                raise ValidationFailure(
                    f"{target_id}: opening presentation_form differs from plan"
                )
            validate_presentation_text(hook_text, planned_form, f"{target_id}.opening_hook")
        constraints = plans[target_id]["plan"]["constraints"]
        if len(hook["text"]) > constraints["opening_max_chars"]:
            raise ValidationFailure(f"{target_id}: opening hook exceeds plan length")
        if len(question["text"]) > constraints["question_max_chars"]:
            raise ValidationFailure(f"{target_id}: closing question exceeds plan length")
        checks = require(item, "self_check", target_id, dict)
        for key in (
            "grounded",
            "purpose_fulfilled",
            "voice_consistent",
            "non_redundant",
            "spoiler_safe",
            "length_ok",
        ):
            if checks.get(key) is not True:
                raise ValidationFailure(f"{target_id}.self_check.{key} must be true")
        if require_third_stage_checks:
            for key in THIRD_STAGE_CHECKS:
                if checks.get(key) is not True:
                    raise ValidationFailure(f"{target_id}.self_check.{key} must be true")
        if require_v04_delivery:
            analogy_used = plans[target_id]["plan"]["analogy"]["use"]
            validate_v04_checks(checks, analogy_used, f"{target_id}.self_check")
        if require_v05_reward:
            planned_reward = plans[target_id]["plan"]["reward_design"]
            delivery = require(item, "reward_delivery", target_id, dict)
            copied_fields = (
                "hook_function",
                "payoff_checkpoint_id",
                "emotional_target",
                "closing_function",
            )
            for key in copied_fields:
                if delivery.get(key) != planned_reward.get(key):
                    raise ValidationFailure(
                        f"{target_id}.reward_delivery.{key} differs from stage 2"
                    )
            validate_v05_checks(
                checks,
                V05_UNIT_CHECKS,
                f"{target_id}.self_check",
            )
        if require_v06_style:
            validate_v05_checks(
                checks,
                V06_UNIT_STYLE_CHECKS,
                f"{target_id}.self_check",
            )


def validate_beat_difficulties(
    items: dict[str, dict[str, Any]],
    require_v05_reward: bool,
    beat_neighbors: dict[str, dict[str, str | None]],
) -> None:
    for target_id, item in items.items():
        if require_v05_reward:
            context_used = require(item, "context_used", target_id, dict)
            for key in ("previous_id", "next_id", "second_next_id"):
                if key not in context_used:
                    raise ValidationFailure(f"{target_id}.context_used: missing {key}")
                if context_used.get(key) != beat_neighbors[target_id][key]:
                    raise ValidationFailure(
                        f"{target_id}.context_used.{key} does not match source siblings"
                    )
        difficulty = require(item, "difficulty", target_id, dict)
        dimensions = require(difficulty, "dimensions", f"{target_id}.difficulty", dict)
        values: list[int] = []
        for key in DIMENSIONS:
            value = dimensions.get(key)
            if type(value) is not int or not 0 <= value <= 2:
                raise ValidationFailure(f"{target_id}: {key} must be integer 0..2")
            values.append(value)
        score = difficulty.get("score")
        if type(score) is not int or score != sum(values):
            raise ValidationFailure(f"{target_id}: score must equal dimension sum")
        level = difficulty.get("level")
        if level != expected_level(score):
            raise ValidationFailure(f"{target_id}: difficulty level does not match score")
        require_text(difficulty, "rationale", f"{target_id}.difficulty")
        require_text(difficulty, "interest_seed", f"{target_id}.difficulty")


def validate_v05_beat_reward_plan(
    plan: dict[str, Any],
    target_id: str,
    neighbors: dict[str, str | None],
) -> None:
    where = f"{target_id}.plan"
    brief = require(plan, "commentary_brief", where, dict)
    for field in (
        "reader_old_belief",
        "central_question",
        "tension",
        "information_turn",
    ):
        require_text(brief, field, f"{where}.commentary_brief")

    payoff = require(brief, "payoff", f"{where}.commentary_brief", dict)
    validate_enum(
        payoff.get("type"), PAYOFF_TYPES, f"{where}.commentary_brief.payoff.type"
    )
    require_text(payoff, "statement", f"{where}.commentary_brief.payoff")
    validate_enum(
        brief.get("emotional_target"),
        EMOTIONAL_TARGETS,
        f"{where}.commentary_brief.emotional_target",
    )

    tags = require(brief, "function_tags", f"{where}.commentary_brief", dict)
    validate_function_tags(tags, f"{where}.commentary_brief.function_tags")
    forbidden = require(
        brief, "forbidden_exaggeration", f"{where}.commentary_brief", list
    )
    if not forbidden:
        raise ValidationFailure(
            f"{where}.commentary_brief.forbidden_exaggeration must not be empty"
        )
    for index, value in enumerate(forbidden):
        if not isinstance(value, str) or not value.strip():
            raise ValidationFailure(
                f"{where}.commentary_brief.forbidden_exaggeration[{index}] "
                "must be non-empty text"
            )

    if "next_dependency" not in brief:
        raise ValidationFailure(f"{where}.commentary_brief: missing next_dependency")
    dependency = brief["next_dependency"]
    expected_next = neighbors["next_id"]
    if dependency is not None:
        if not isinstance(dependency, dict):
            raise ValidationFailure(
                f"{where}.commentary_brief.next_dependency must be an object or null"
            )
        if dependency.get("target_id") != expected_next or expected_next is None:
            raise ValidationFailure(
                f"{where}.commentary_brief.next_dependency.target_id "
                "must be the immediate next sibling"
            )
        require_text(
            dependency, "relationship", f"{where}.commentary_brief.next_dependency"
        )
        require_text(
            dependency, "bridge_question", f"{where}.commentary_brief.next_dependency"
        )
        validate_evidence_refs(
            dependency.get("evidence_refs"),
            expected_next,
            f"{where}.commentary_brief.next_dependency.evidence_refs",
            require_nonempty=True,
        )

    loop = require(plan, "loop_contract", where, dict)
    action = validate_enum(
        loop.get("action"), LOOP_ACTIONS, f"{where}.loop_contract.action"
    )
    if "next_question" not in loop:
        raise ValidationFailure(f"{where}.loop_contract: missing next_question")
    if "close_by_target_id" not in loop:
        raise ValidationFailure(f"{where}.loop_contract: missing close_by_target_id")
    close_evidence = require(
        loop, "close_by_evidence_refs", f"{where}.loop_contract", list
    )

    if action == "close":
        if dependency is not None:
            raise ValidationFailure(
                f"{where}.loop_contract close action requires a null next_dependency"
            )
        if loop["next_question"] is not None or loop["close_by_target_id"] is not None:
            raise ValidationFailure(
                f"{where}.loop_contract close action requires null next fields"
            )
        if close_evidence:
            raise ValidationFailure(
                f"{where}.loop_contract close action requires empty checkpoint evidence"
            )
        return

    if dependency is None:
        raise ValidationFailure(
            f"{where}.loop_contract close_and_open requires next_dependency"
        )
    if loop["next_question"] != dependency["bridge_question"]:
        raise ValidationFailure(
            f"{where}.loop_contract.next_question differs from bridge_question"
        )
    close_by = loop["close_by_target_id"]
    allowed_close_ids = {neighbors["next_id"], neighbors["second_next_id"]} - {None}
    if close_by not in allowed_close_ids:
        raise ValidationFailure(
            f"{where}.loop_contract.close_by_target_id exceeds the two-beat horizon"
        )
    validate_evidence_refs(
        close_evidence,
        close_by,
        f"{where}.loop_contract.close_by_evidence_refs",
        require_nonempty=True,
    )


def validate_v06_delivery_design(plan: dict[str, Any], target_id: str) -> None:
    where = f"{target_id}.plan.delivery_design"
    design = require(plan, "delivery_design", f"{target_id}.plan", dict)
    require_text(design, "human_anchor", where)
    require_text(design, "reader_reaction", where)
    require_text(plan, "form_rationale", f"{target_id}.plan")
    lively_turn = require(design, "lively_turn", where, dict)
    device = validate_enum(
        lively_turn.get("device"),
        LIVELY_TURN_DEVICES,
        f"{where}.lively_turn.device",
    )
    if device == "none":
        if (
            lively_turn.get("source_relationship") is not None
            or lively_turn.get("planned_move") is not None
        ):
            raise ValidationFailure(
                f"{where}.lively_turn none device requires null relationship and move"
            )
    else:
        require_text(lively_turn, "source_relationship", f"{where}.lively_turn")
        require_text(lively_turn, "planned_move", f"{where}.lively_turn")

    dependency = plan["commentary_brief"]["next_dependency"]
    if dependency is not None:
        require_text(
            dependency,
            "reader_need",
            f"{target_id}.plan.commentary_brief.next_dependency",
        )
        require_text(
            dependency,
            "why_current_stops",
            f"{target_id}.plan.commentary_brief.next_dependency",
        )


def validate_v07_delivery_design(comment_plan: dict[str, Any], where: str) -> None:
    design = require(comment_plan, "delivery_design", where, dict)
    design_where = f"{where}.delivery_design"
    require_text(design, "human_anchor", design_where)
    require_text(design, "reader_reaction", design_where)
    require_text(comment_plan, "form_rationale", where)
    lively_turn = require(design, "lively_turn", design_where, dict)
    device = validate_enum(
        lively_turn.get("device"),
        LIVELY_TURN_DEVICES,
        f"{design_where}.lively_turn.device",
    )
    if device == "none":
        if (
            lively_turn.get("source_relationship") is not None
            or lively_turn.get("planned_move") is not None
        ):
            raise ValidationFailure(
                f"{design_where}.lively_turn none device requires null "
                "relationship and move"
            )
    else:
        require_text(lively_turn, "source_relationship", f"{design_where}.lively_turn")
        require_text(lively_turn, "planned_move", f"{design_where}.lively_turn")


def validate_v07_comment_plan(
    comment_plan: dict[str, Any], where: str, allowed_strategies: set[str]
) -> str:
    voice = validate_enum(comment_plan.get("voice"), VOICES, f"{where}.voice")
    expected_type = "roast" if voice == "student" else "fun_commentary"
    if comment_plan.get("comment_type") != expected_type:
        raise ValidationFailure(
            f"{where}.comment_type must be {expected_type!r} for {voice}"
        )
    require_text(comment_plan, "contribution", where)
    validate_enum(comment_plan.get("strategy"), allowed_strategies, f"{where}.strategy")
    if "roast_move" not in comment_plan:
        raise ValidationFailure(f"{where}: missing roast_move")
    if voice == "student":
        validate_enum(comment_plan.get("roast_move"), ROAST_MOVES, f"{where}.roast_move")
    elif comment_plan.get("roast_move") is not None:
        raise ValidationFailure(f"{where}.roast_move must be null for mentor")

    validate_delivery_plan(comment_plan, where)
    validate_v07_delivery_design(comment_plan, where)
    tone_tags = require(comment_plan, "tone_tags", where, list)
    if not tone_tags:
        raise ValidationFailure(f"{where}.tone_tags must not be empty")
    for index, tag in enumerate(tone_tags):
        if not isinstance(tag, str) or not tag.strip():
            raise ValidationFailure(f"{where}.tone_tags[{index}] must be non-empty text")

    constraints = require(comment_plan, "constraints", where, dict)
    require(constraints, "must", f"{where}.constraints", list)
    require(constraints, "avoid", f"{where}.constraints", list)
    if "min_chars" in constraints:
        raise ValidationFailure(f"{where}.constraints must not include min_chars")
    max_chars = constraints.get("max_chars")
    if type(max_chars) is not int or max_chars <= 0:
        raise ValidationFailure(f"{where}.constraints.max_chars must be positive")
    return voice


def validate_v07_pairing_design(plan: dict[str, Any], voices: list[str], where: str) -> None:
    if "pairing_design" not in plan:
        raise ValidationFailure(f"{where}: missing pairing_design")
    pairing = plan["pairing_design"]
    if len(voices) == 1:
        if pairing is not None:
            raise ValidationFailure(f"{where}.pairing_design must be null for one voice")
        return
    if not isinstance(pairing, dict):
        raise ValidationFailure(f"{where}.pairing_design must be an object when paired")
    for field in ("mentor_job", "student_job", "non_overlap"):
        require_text(pairing, field, f"{where}.pairing_design")


def validate_v07_chapter_coverage(
    items: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
    coverage_target: dict[str, Any],
    *,
    collection_key: str,
    stage_label: str,
) -> None:
    chapters: dict[str, list[set[str]]] = {}
    for target_id, item in items.items():
        chapter_id = difficulties[target_id]["context_used"].get("chapter_id") or "unknown"
        container = item["plan"] if collection_key == "comment_plans" else item
        entries = container[collection_key]
        voices = {entry["voice"] for entry in entries}
        chapters.setdefault(chapter_id, []).append(voices)

    for chapter_id, voice_sets in chapters.items():
        total = len(voice_sets)
        for voice in ("mentor", "student"):
            actual = sum(voice in voices for voices in voice_sets)
            required = math.ceil(total * coverage_target[voice])
            if actual < required:
                raise ValidationFailure(
                    f"{stage_label} {chapter_id}: {voice} covers {actual}/{total} beats; "
                    f"requires at least {required}"
                )


def validate_beat_plans(
    items: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
    require_voice_locked_types: bool,
    require_v04_delivery: bool,
    require_v05_reward: bool,
    require_v06_delivery_design: bool,
    beat_neighbors: dict[str, dict[str, str | None]],
) -> None:
    for target_id, item in items.items():
        level = difficulties[target_id]["difficulty"]["level"]
        if item.get("difficulty_level") != level:
            raise ValidationFailure(f"{target_id}: difficulty_level differs from stage 4")
        plan = require(item, "plan", target_id, dict)
        expected_mode = "fun_brief" if level == "simple" else "fun_explanation"
        if plan.get("mode") != expected_mode:
            raise ValidationFailure(f"{target_id}: mode must be {expected_mode}")
        voice = require_text(plan, "voice", f"{target_id}.plan")
        if voice not in VOICES:
            raise ValidationFailure(f"{target_id}: invalid plan voice")
        if require_voice_locked_types:
            expected_type = "roast" if voice == "student" else "fun_commentary"
            if plan.get("comment_type") != expected_type:
                raise ValidationFailure(
                    f"{target_id}: {voice} plan comment_type must be {expected_type}"
                )
        require_text(plan, "primary_goal", f"{target_id}.plan")
        require_text(plan, "angle", f"{target_id}.plan")
        if require_v04_delivery:
            validate_delivery_plan(plan, f"{target_id}.plan")
        if require_v05_reward:
            validate_v05_beat_reward_plan(plan, target_id, beat_neighbors[target_id])
        if require_v06_delivery_design:
            validate_v06_delivery_design(plan, target_id)
        tone_tags = require(plan, "tone_tags", f"{target_id}.plan", list)
        if not tone_tags:
            raise ValidationFailure(f"{target_id}: tone_tags must not be empty")
        constraints = require(plan, "constraints", f"{target_id}.plan", dict)
        require(constraints, "must", f"{target_id}.plan.constraints", list)
        require(constraints, "avoid", f"{target_id}.plan.constraints", list)
        max_chars = constraints.get("max_chars")
        if type(max_chars) is not int or max_chars <= 0:
            raise ValidationFailure(f"{target_id}: max_chars must be a positive integer")
        if require_v04_delivery:
            if "min_chars" in constraints:
                raise ValidationFailure(
                    f"{target_id}: schema 0.4.0+ must not include min_chars"
                )
        elif require_voice_locked_types:
            min_chars = constraints.get("min_chars")
            if type(min_chars) is not int or min_chars <= 0:
                raise ValidationFailure(f"{target_id}: min_chars must be a positive integer")
            if min_chars > max_chars:
                raise ValidationFailure(f"{target_id}: min_chars must not exceed max_chars")
            if voice == "mentor" and level == "medium" and max_chars < 180:
                raise ValidationFailure(
                    f"{target_id}: medium mentor max_chars must be at least 180"
                )
            if voice == "mentor" and level == "hard" and max_chars < 220:
                raise ValidationFailure(
                    f"{target_id}: hard mentor max_chars must be at least 220"
                )


def validate_v07_beat_plans(
    items: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
    beat_neighbors: dict[str, dict[str, str | None]],
    coverage_target: dict[str, Any],
) -> None:
    for target_id, item in items.items():
        level = difficulties[target_id]["difficulty"]["level"]
        if item.get("difficulty_level") != level:
            raise ValidationFailure(f"{target_id}: difficulty_level differs from stage 4")
        plan = require(item, "plan", target_id, dict)
        where = f"{target_id}.plan"
        expected_mode = "fun_brief" if level == "simple" else "fun_explanation"
        if plan.get("mode") != expected_mode:
            raise ValidationFailure(f"{target_id}: mode must be {expected_mode}")
        require_text(plan, "primary_goal", where)
        require_text(plan, "angle", where)

        validate_v05_beat_reward_plan(plan, target_id, beat_neighbors[target_id])
        dependency = plan["commentary_brief"]["next_dependency"]
        if dependency is not None:
            require_text(
                dependency,
                "reader_need",
                f"{where}.commentary_brief.next_dependency",
            )
            require_text(
                dependency,
                "why_current_stops",
                f"{where}.commentary_brief.next_dependency",
            )

        comment_plans = require(plan, "comment_plans", where, list)
        if not 1 <= len(comment_plans) <= 2:
            raise ValidationFailure(f"{where}.comment_plans must contain one or two entries")
        voices: list[str] = []
        allowed_strategies = (
            FUN_BRIEF_STRATEGIES
            if expected_mode == "fun_brief"
            else FUN_EXPLANATION_STRATEGIES
        )
        for index, comment_plan in enumerate(comment_plans):
            entry_where = f"{where}.comment_plans[{index}]"
            if not isinstance(comment_plan, dict):
                raise ValidationFailure(f"{entry_where} must be an object")
            voices.append(
                validate_v07_comment_plan(
                    comment_plan,
                    entry_where,
                    allowed_strategies,
                )
            )
        allowed_voice_orders = [["mentor"], ["student"], ["mentor", "student"]]
        if voices not in allowed_voice_orders:
            raise ValidationFailure(
                f"{where}.comment_plans voices must be mentor, student, or mentor then student"
            )
        validate_v07_pairing_design(plan, voices, where)
        if plan["loop_contract"]["action"] == "close_and_open" and "mentor" not in voices:
            raise ValidationFailure(f"{where}: close_and_open requires a mentor plan")

    validate_v07_chapter_coverage(
        items,
        difficulties,
        coverage_target,
        collection_key="comment_plans",
        stage_label="beat_plans",
    )


def report_v06_chapter_style(
    plans: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
) -> None:
    chapters: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for target_id, item in plans.items():
        chapter_id = difficulties[target_id]["context_used"].get("chapter_id") or "unknown"
        chapters.setdefault(chapter_id, []).append((target_id, item["plan"]))

    for chapter_id, entries in chapters.items():
        total = len(entries)
        schematic = sum(
            plan["presentation_form"] in {"arrow_chain", "bullet_breakdown"}
            for _, plan in entries
        )
        opened = sum(
            plan["loop_contract"]["action"] == "close_and_open"
            for _, plan in entries
        )
        print(
            f"STYLE {chapter_id}: schematic_forms={schematic}/{total}, "
            f"opened_loops={opened}/{total}"
        )
        if schematic * 3 > total:
            print(
                f"WARN {chapter_id}: schematic forms exceed one-third; "
                "re-audit each form_rationale"
            )
        if opened * 3 > total:
            print(
                f"WARN {chapter_id}: opened loops exceed one-third; "
                "re-audit bridge necessity"
            )

        for index in range(2, total):
            current = entries[index][1]["presentation_form"]
            if all(
                entries[position][1]["presentation_form"] == current
                for position in range(index - 2, index + 1)
            ):
                target_ids = ", ".join(
                    entries[position][0] for position in range(index - 2, index + 1)
                )
                print(
                    f"WARN {chapter_id}: presentation_form {current!r} repeats "
                    f"across {target_ids}"
                )
        for index in range(1, total):
            previous_open = (
                entries[index - 1][1]["loop_contract"]["action"] == "close_and_open"
            )
            current_open = (
                entries[index][1]["loop_contract"]["action"] == "close_and_open"
            )
            if previous_open and current_open:
                print(
                    f"WARN {chapter_id}: adjacent opened loops at "
                    f"{entries[index - 1][0]}, {entries[index][0]}"
                )


def report_v07_chapter_style(
    plans: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
) -> None:
    chapters: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for target_id, item in plans.items():
        chapter_id = difficulties[target_id]["context_used"].get("chapter_id") or "unknown"
        chapters.setdefault(chapter_id, []).append((target_id, item["plan"]))

    for chapter_id, entries in chapters.items():
        total = len(entries)
        mentor_count = sum(
            any(cp["voice"] == "mentor" for cp in plan["comment_plans"])
            for _, plan in entries
        )
        student_count = sum(
            any(cp["voice"] == "student" for cp in plan["comment_plans"])
            for _, plan in entries
        )
        paired_count = sum(len(plan["comment_plans"]) == 2 for _, plan in entries)
        opened = sum(
            plan["loop_contract"]["action"] == "close_and_open"
            for _, plan in entries
        )
        print(
            f"STYLE {chapter_id}: mentor={mentor_count}/{total}, "
            f"student={student_count}/{total}, paired={paired_count}/{total}, "
            f"opened_loops={opened}/{total}"
        )

        scaffolded: list[str] = []
        for target_id, plan in entries:
            for comment_plan in plan["comment_plans"]:
                if comment_plan["voice"] != "student":
                    continue
                reaction = comment_plan["delivery_design"]["reader_reaction"].lstrip()
                if reaction.startswith(("我以为", "我想", "懂了")):
                    scaffolded.append(target_id)
        if len(scaffolded) > 1:
            print(
                f"WARN {chapter_id}: repeated first-person student scaffold at "
                f"{', '.join(scaffolded)}"
            )

        for voice in ("mentor", "student"):
            voice_entries: list[tuple[str, str]] = []
            for target_id, plan in entries:
                for comment_plan in plan["comment_plans"]:
                    if comment_plan["voice"] == voice:
                        voice_entries.append(
                            (target_id, comment_plan["presentation_form"])
                        )
            for index in range(2, len(voice_entries)):
                window = voice_entries[index - 2 : index + 1]
                if len({form for _, form in window}) == 1:
                    print(
                        f"WARN {chapter_id}: {voice} presentation_form "
                        f"{window[0][1]!r} repeats across "
                        f"{', '.join(target_id for target_id, _ in window)}"
                    )

        roast_entries: list[tuple[str, str]] = []
        for target_id, plan in entries:
            for comment_plan in plan["comment_plans"]:
                if comment_plan["voice"] == "student":
                    roast_entries.append((target_id, comment_plan["roast_move"]))
        for index in range(2, len(roast_entries)):
            window = roast_entries[index - 2 : index + 1]
            if len({move for _, move in window}) == 1:
                print(
                    f"WARN {chapter_id}: student roast_move {window[0][1]!r} "
                    f"repeats across {', '.join(target_id for target_id, _ in window)}"
                )


def validate_beat_comments(
    items: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
    plans: dict[str, dict[str, Any]],
    require_third_stage_checks: bool,
    require_voice_locked_types: bool,
    require_v04_delivery: bool,
    require_v05_reward: bool,
    require_v06_style: bool,
) -> None:
    for target_id, item in items.items():
        level = difficulties[target_id]["difficulty"]["level"]
        plan = plans[target_id]["plan"]
        if item.get("difficulty_level") != level:
            raise ValidationFailure(f"{target_id}: difficulty_level differs from stage 4")
        if item.get("mode") != plan.get("mode"):
            raise ValidationFailure(f"{target_id}: mode differs from stage 5")
        commentary = require(item, "commentary", target_id, dict)
        commentary_text = require_text(commentary, "text", f"{target_id}.commentary")
        voice = commentary.get("voice")
        if voice != plan.get("voice"):
            raise ValidationFailure(f"{target_id}: commentary voice differs from plan")
        if require_voice_locked_types:
            expected_type = "roast" if voice == "student" else "fun_commentary"
            if plan.get("comment_type") != expected_type:
                raise ValidationFailure(
                    f"{target_id}: stage 5 comment_type differs from planned voice"
                )
            if item.get("comment_type") != expected_type:
                raise ValidationFailure(
                    f"{target_id}: {voice} commentary comment_type must be {expected_type}"
                )
            if not require_v04_delivery:
                min_chars = plan["constraints"].get("min_chars")
                if type(min_chars) is not int or len(commentary_text) < min_chars:
                    raise ValidationFailure(
                        f"{target_id}: commentary is shorter than plan minimum"
                    )
        if require_v04_delivery:
            planned_form = plan["presentation_form"]
            if item.get("presentation_form") != planned_form:
                raise ValidationFailure(
                    f"{target_id}: commentary presentation_form differs from plan"
                )
            validate_presentation_text(commentary_text, planned_form, f"{target_id}.commentary")
        if len(commentary_text) > plan["constraints"]["max_chars"]:
            raise ValidationFailure(f"{target_id}: commentary exceeds plan length")
        checks = require(item, "self_check", target_id, dict)
        for key in (
            "grounded",
            "purpose_fulfilled",
            "voice_consistent",
            "non_redundant",
            "length_ok",
        ):
            if checks.get(key) is not True:
                raise ValidationFailure(f"{target_id}.self_check.{key} must be true")
        if require_third_stage_checks:
            for key in THIRD_STAGE_CHECKS:
                if checks.get(key) is not True:
                    raise ValidationFailure(f"{target_id}.self_check.{key} must be true")
        if require_voice_locked_types and checks.get("voice_goal_fulfilled") is not True:
            raise ValidationFailure(
                f"{target_id}.self_check.voice_goal_fulfilled must be true"
            )
        if require_v04_delivery:
            analogy_used = plan["analogy"]["use"]
            validate_v04_checks(checks, analogy_used, f"{target_id}.self_check")
        if require_v05_reward:
            brief = plan["commentary_brief"]
            loop = plan["loop_contract"]
            dependency = brief["next_dependency"]
            delivery = require(item, "reward_delivery", target_id, dict)
            expected_delivery = {
                "payoff_type": brief["payoff"]["type"],
                "emotional_target": brief["emotional_target"],
                "function_tags": brief["function_tags"],
                "loop_action": loop["action"],
                "next_dependency_target_id": (
                    dependency["target_id"] if dependency is not None else None
                ),
                "close_by_target_id": loop["close_by_target_id"],
            }
            for key, expected in expected_delivery.items():
                if key not in delivery:
                    raise ValidationFailure(
                        f"{target_id}.reward_delivery: missing {key}"
                    )
                if delivery[key] != expected:
                    raise ValidationFailure(
                        f"{target_id}.reward_delivery.{key} differs from stage 5"
                    )
            validate_v05_checks(
                checks,
                V05_REWARD_CHECKS,
                f"{target_id}.self_check",
            )
        if require_v06_style:
            validate_v05_checks(
                checks,
                V06_BEAT_STYLE_CHECKS,
                f"{target_id}.self_check",
            )
        addresses = checks.get("addresses_difficulty")
        if level == "simple" and addresses is not None:
            raise ValidationFailure(f"{target_id}: simple beat addresses_difficulty must be null")
        if level != "simple" and addresses is not True:
            raise ValidationFailure(f"{target_id}: explanation must address difficulty")


def validate_v07_commentary_entry(
    commentary: dict[str, Any],
    planned: dict[str, Any],
    level: str,
    *,
    paired: bool,
    loop: dict[str, Any],
    where: str,
) -> None:
    voice = planned["voice"]
    for field in ("voice", "comment_type", "contribution", "presentation_form"):
        if commentary.get(field) != planned.get(field):
            raise ValidationFailure(f"{where}.{field} differs from stage 5")
    expected_type = "roast" if voice == "student" else "fun_commentary"
    if commentary.get("comment_type") != expected_type:
        raise ValidationFailure(
            f"{where}.comment_type must be {expected_type!r} for {voice}"
        )

    text = require_text(commentary, "text", where)
    validate_presentation_text(text, planned["presentation_form"], where)
    if len(text) > planned["constraints"]["max_chars"]:
        raise ValidationFailure(f"{where}.text exceeds planned max_chars")

    checks = require(commentary, "self_check", where, dict)
    for key in (
        "grounded",
        "purpose_fulfilled",
        "voice_consistent",
        "non_redundant",
        "length_ok",
        "voice_goal_fulfilled",
        *THIRD_STAGE_CHECKS,
    ):
        if checks.get(key) is not True:
            raise ValidationFailure(f"{where}.self_check.{key} must be true")
    validate_v04_checks(
        checks,
        planned["analogy"]["use"],
        f"{where}.self_check",
    )
    validate_v05_checks(checks, V05_REWARD_CHECKS, f"{where}.self_check")
    validate_v05_checks(checks, V06_BEAT_STYLE_CHECKS, f"{where}.self_check")

    addresses = checks.get("addresses_difficulty")
    if level == "simple" and addresses is not None:
        raise ValidationFailure(f"{where}.self_check.addresses_difficulty must be null")
    if level != "simple" and addresses is not True:
        raise ValidationFailure(f"{where}.self_check.addresses_difficulty must be true")

    if voice == "student":
        validate_v05_checks(checks, V07_STUDENT_CHECKS, f"{where}.self_check")
        if loop["action"] == "close_and_open":
            next_question = loop["next_question"]
            if next_question and next_question in text:
                raise ValidationFailure(
                    f"{where}.text must not copy the shared bridge question"
                )
            if text.rstrip().endswith(("?", "？")):
                raise ValidationFailure(
                    f"{where}.text must end on the roast, not a bridge question"
                )
    else:
        for key in V07_STUDENT_CHECKS:
            if checks.get(key) is not None:
                raise ValidationFailure(f"{where}.self_check.{key} must be null for mentor")

    pair_value = checks.get("pair_complementary")
    if paired and pair_value is not True:
        raise ValidationFailure(f"{where}.self_check.pair_complementary must be true")
    if not paired and pair_value is not None:
        raise ValidationFailure(f"{where}.self_check.pair_complementary must be null")


def validate_v07_beat_comments(
    items: dict[str, dict[str, Any]],
    difficulties: dict[str, dict[str, Any]],
    plans: dict[str, dict[str, Any]],
    coverage_target: dict[str, Any],
) -> None:
    for target_id, item in items.items():
        level = difficulties[target_id]["difficulty"]["level"]
        plan = plans[target_id]["plan"]
        if item.get("difficulty_level") != level:
            raise ValidationFailure(f"{target_id}: difficulty_level differs from stage 4")
        if item.get("mode") != plan.get("mode"):
            raise ValidationFailure(f"{target_id}: mode differs from stage 5")

        planned_comments = plan["comment_plans"]
        commentaries = require(item, "commentaries", target_id, list)
        if len(commentaries) != len(planned_comments):
            raise ValidationFailure(
                f"{target_id}.commentaries must match stage-5 comment_plans length"
            )
        paired = len(commentaries) == 2
        for index, (commentary, planned) in enumerate(
            zip(commentaries, planned_comments, strict=True)
        ):
            where = f"{target_id}.commentaries[{index}]"
            if not isinstance(commentary, dict):
                raise ValidationFailure(f"{where} must be an object")
            validate_v07_commentary_entry(
                commentary,
                planned,
                level,
                paired=paired,
                loop=plan["loop_contract"],
                where=where,
            )

        if plan["loop_contract"]["action"] == "close_and_open":
            next_question = plan["loop_contract"]["next_question"]
            mentor_text = next(
                commentary["text"]
                for commentary in commentaries
                if commentary["voice"] == "mentor"
            )
            if next_question not in mentor_text:
                raise ValidationFailure(
                    f"{target_id}: mentor text must realize loop_contract.next_question"
                )

        if "pair_check" not in item:
            raise ValidationFailure(f"{target_id}: missing pair_check")
        pair_check = item["pair_check"]
        if paired:
            if not isinstance(pair_check, dict):
                raise ValidationFailure(f"{target_id}.pair_check must be an object")
            require_text(pair_check, "mentor_reward", f"{target_id}.pair_check")
            require_text(pair_check, "student_reward", f"{target_id}.pair_check")
            if pair_check.get("non_redundant") is not True:
                raise ValidationFailure(f"{target_id}.pair_check.non_redundant must be true")
        elif pair_check is not None:
            raise ValidationFailure(f"{target_id}.pair_check must be null for one voice")

        brief = plan["commentary_brief"]
        loop = plan["loop_contract"]
        dependency = brief["next_dependency"]
        delivery = require(item, "reward_delivery", target_id, dict)
        expected_delivery = {
            "payoff_type": brief["payoff"]["type"],
            "emotional_target": brief["emotional_target"],
            "function_tags": brief["function_tags"],
            "loop_action": loop["action"],
            "next_dependency_target_id": (
                dependency["target_id"] if dependency is not None else None
            ),
            "close_by_target_id": loop["close_by_target_id"],
        }
        for key, expected in expected_delivery.items():
            if key not in delivery:
                raise ValidationFailure(f"{target_id}.reward_delivery: missing {key}")
            if delivery[key] != expected:
                raise ValidationFailure(
                    f"{target_id}.reward_delivery.{key} differs from stage 5"
                )

    validate_v07_chapter_coverage(
        items,
        difficulties,
        coverage_target,
        collection_key="commentaries",
        stage_label="beat_comments",
    )


def validate_artifacts(
    source: dict[str, Any],
    units: list[dict[str, Any]],
    beats: list[dict[str, Any]],
    artifacts_dir: Path,
    through: int,
) -> None:
    unit_ids = [item["id"] for item in units]
    beat_ids = [item["id"] for item in beats]
    unit_child_ids = build_unit_child_ids(units)
    beat_neighbors = build_beat_neighbors(beats)
    loaded: dict[str, dict[str, dict[str, Any]]] = {}
    run_schema_version: str | None = None
    v07_settings: dict[str, Any] | None = None

    for index, (filename, stage_name, target_kind) in enumerate(STAGES[:through], start=1):
        path = artifacts_dir / filename
        artifact = load_json(path)
        schema_version = artifact.get("schema_version")
        if run_schema_version is None:
            run_schema_version = schema_version
        elif (
            run_schema_version == "0.7.0" or schema_version == "0.7.0"
        ) and schema_version != run_schema_version:
            raise ValidationFailure(
                f"{path.name}: schema 0.7.0 artifacts must not mix with legacy schemas"
            )
        is_v07 = schema_version == "0.7.0"
        require_third_stage_checks = schema_version in {
            "0.2.0",
            "0.3.0",
            "0.4.0",
            "0.5.0",
            "0.6.0",
            "0.7.0",
        }
        require_voice_locked_types = schema_version in {
            "0.3.0",
            "0.4.0",
            "0.5.0",
            "0.6.0",
            "0.7.0",
        }
        require_v04_delivery = schema_version in {
            "0.4.0",
            "0.5.0",
            "0.6.0",
            "0.7.0",
        }
        require_v05_reward = schema_version in {"0.5.0", "0.6.0", "0.7.0"}
        require_v06_delivery_design = schema_version in {"0.6.0", "0.7.0"}
        require_v06_style = schema_version in {"0.6.0", "0.7.0"}
        ids = unit_ids if target_kind == "unit" else beat_ids
        items = validate_envelope(artifact, stage_name, source, ids, path)
        if is_v07:
            current_settings = {
                "unit_voice_policy": artifact["settings"]["unit_voice_policy"],
                "beat_voice_policy": artifact["settings"]["beat_voice_policy"],
                "voice_coverage_target": artifact["settings"]["voice_coverage_target"],
            }
            if v07_settings is None:
                v07_settings = current_settings
            elif current_settings != v07_settings:
                raise ValidationFailure(
                    f"{path.name}: schema 0.7.0 voice settings differ from earlier stages"
                )
        loaded[stage_name] = items

        if stage_name == "unit_conflicts":
            validate_unit_conflicts(items)
        elif stage_name == "unit_plans":
            conflicts = loaded["unit_conflicts"]
            allowed_checkpoints = {
                target_id: [
                    child_id
                    for child_id in child_ids
                    if child_id not in conflicts
                    or conflicts[child_id].get("eligibility") != "skip"
                ][:2]
                for target_id, child_ids in unit_child_ids.items()
            }
            validate_unit_plans(
                items,
                conflicts,
                require_v04_delivery,
                require_v05_reward,
                require_v06_delivery_design,
                allowed_checkpoints,
            )
        elif stage_name == "unit_comments":
            validate_unit_comments(
                items,
                loaded["unit_plans"],
                require_third_stage_checks,
                require_v04_delivery,
                require_v05_reward,
                require_v06_style,
            )
        elif stage_name == "beat_difficulties":
            validate_beat_difficulties(items, require_v05_reward, beat_neighbors)
        elif stage_name == "beat_plans":
            if is_v07:
                validate_v07_beat_plans(
                    items,
                    loaded["beat_difficulties"],
                    beat_neighbors,
                    artifact["settings"]["voice_coverage_target"],
                )
                report_v07_chapter_style(items, loaded["beat_difficulties"])
            else:
                validate_beat_plans(
                    items,
                    loaded["beat_difficulties"],
                    require_voice_locked_types,
                    require_v04_delivery,
                    require_v05_reward,
                    require_v06_delivery_design,
                    beat_neighbors,
                )
            if require_v06_delivery_design and not is_v07:
                report_v06_chapter_style(items, loaded["beat_difficulties"])
        elif stage_name == "beat_comments":
            if is_v07:
                validate_v07_beat_comments(
                    items,
                    loaded["beat_difficulties"],
                    loaded["beat_plans"],
                    artifact["settings"]["voice_coverage_target"],
                )
            else:
                validate_beat_comments(
                    items,
                    loaded["beat_difficulties"],
                    loaded["beat_plans"],
                    require_third_stage_checks,
                    require_voice_locked_types,
                    require_v04_delivery,
                    require_v05_reward,
                    require_v06_style,
                )
        print(f"OK stage {index}: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="segmentation JSON")
    parser.add_argument("--artifacts-dir", type=Path, help="directory containing stage JSON files")
    parser.add_argument("--through", type=int, choices=range(1, 7), default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source = load_json(args.input)
        units, beats = validate_source(source)
        print(f"OK input: {args.input} ({len(units)} units, {len(beats)} beats)")
        if args.artifacts_dir is not None:
            validate_artifacts(source, units, beats, args.artifacts_dir, args.through)
        elif args.through != 6:
            raise ValidationFailure("--through requires --artifacts-dir")
    except ValidationFailure as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
