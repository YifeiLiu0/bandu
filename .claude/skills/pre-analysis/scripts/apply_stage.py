#!/usr/bin/env python3
"""Insert one pre-analysis stage without reserializing existing JSON text."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Member:
    key: str
    key_start: int
    value: "Node"
    comma: int | None


@dataclass
class Node:
    kind: str
    start: int
    end: int
    scalar: Any = None
    members: list[Member] = field(default_factory=list)
    elements: list["Node"] = field(default_factory=list)

    def member(self, key: str) -> Member | None:
        return next((item for item in self.members if item.key == key), None)


class JsonPositions:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)

    def parse(self) -> Node:
        node, index = self._value(self._ws(0))
        if self._ws(index) != self.length:
            raise ValueError("Trailing content after JSON value")
        return node

    def _ws(self, index: int) -> int:
        while index < self.length and self.text[index] in " \t\r\n":
            index += 1
        return index

    def _string_end(self, index: int) -> int:
        if self.text[index] != '"':
            raise ValueError(f"Expected string at offset {index}")
        index += 1
        while index < self.length:
            char = self.text[index]
            if char == "\\":
                index += 2
            elif char == '"':
                return index + 1
            else:
                index += 1
        raise ValueError("Unterminated JSON string")

    def _value(self, index: int) -> tuple[Node, int]:
        index = self._ws(index)
        start = index
        char = self.text[index]
        if char == "{":
            return self._object(index)
        if char == "[":
            return self._array(index)
        if char == '"':
            end = self._string_end(index)
            return Node("scalar", start, end, json.loads(self.text[start:end])), end
        end = index
        while end < self.length and self.text[end] not in ",]} \t\r\n":
            end += 1
        return Node("scalar", start, end, json.loads(self.text[start:end])), end

    def _object(self, index: int) -> tuple[Node, int]:
        start = index
        index = self._ws(index + 1)
        members: list[Member] = []
        if self.text[index] == "}":
            return Node("object", start, index + 1, members=members), index + 1
        while True:
            key_start = index
            key_end = self._string_end(index)
            key = json.loads(self.text[key_start:key_end])
            index = self._ws(key_end)
            if self.text[index] != ":":
                raise ValueError(f"Expected colon at offset {index}")
            value, index = self._value(index + 1)
            index = self._ws(index)
            comma = None
            if self.text[index] == ",":
                comma = index
                index = self._ws(index + 1)
            elif self.text[index] == "}":
                members.append(Member(key, key_start, value, comma))
                return Node("object", start, index + 1, members=members), index + 1
            else:
                raise ValueError(f"Expected comma or object end at offset {index}")
            members.append(Member(key, key_start, value, comma))

    def _array(self, index: int) -> tuple[Node, int]:
        start = index
        index = self._ws(index + 1)
        elements: list[Node] = []
        if self.text[index] == "]":
            return Node("array", start, index + 1, elements=elements), index + 1
        while True:
            value, index = self._value(index)
            elements.append(value)
            index = self._ws(index)
            if self.text[index] == ",":
                index = self._ws(index + 1)
            elif self.text[index] == "]":
                return Node("array", start, index + 1, elements=elements), index + 1
            else:
                raise ValueError(f"Expected comma or array end at offset {index}")


def walk_objects(node: Node):
    if node.kind == "object":
        yield node
        for member in node.members:
            yield from walk_objects(member.value)
    elif node.kind == "array":
        for element in node.elements:
            yield from walk_objects(element)


def collect_targets(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    structural: list[str] = []
    beats: list[str] = []

    def visit_beat(beat: dict[str, Any]) -> None:
        beats.append(beat["id"])

    def visit_section(section: dict[str, Any]) -> None:
        structural.append(section["id"])
        for beat in section.get("beats", []):
            visit_beat(beat)
        for subsection in section.get("subsections", []):
            structural.append(subsection["id"])
            for beat in subsection.get("beats", []):
                visit_beat(beat)

    book = data["book"]
    structural.append(book["id"])
    for chapter in book["chapters"]:
        structural.append(chapter["id"])
        for section in chapter["sections"]:
            visit_section(section)
    return structural, beats


STAGES = {
    "unit_conflicts": ("structural", "conflict", ("flow", "function", "summary", "title", "id")),
    "unit_plans": ("structural", "plan", ("conflict",)),
    "beat_difficulties": ("beats", "difficulty", ("function",)),
    "beat_plans": ("beats", "plan", ("difficulty",)),
}


def insertion_text(text: str, obj: Node, anchor: Member, key: str, value: Any) -> tuple[int, str]:
    newline = "\r\n" if "\r\n" in text else "\n"
    multiline = "\n" in text[obj.start:obj.end]
    if not multiline:
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if anchor.comma is not None:
            return anchor.comma + 1, f'"{key}":{rendered},'
        return anchor.value.end, f',"{key}":{rendered}'

    line_start = max(text.rfind("\n", 0, anchor.key_start), text.rfind("\r", 0, anchor.key_start)) + 1
    indent = text[line_start:anchor.key_start]
    rendered = json.dumps(value, ensure_ascii=False, indent=2)
    rendered = rendered.replace("\n", newline + indent)
    addition = f'{newline}{indent}"{key}": {rendered}'
    if anchor.comma is not None:
        return anchor.comma + 1, addition + ","
    return anchor.value.end, "," + addition


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("working_json", type=Path)
    parser.add_argument("stage_patch", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    text = args.working_json.read_bytes().decode("utf-8")
    data = json.loads(text)
    patch = json.loads(args.stage_patch.read_bytes().decode("utf-8"))
    stage = patch.get("stage")
    if stage not in STAGES:
        raise SystemExit(f"Unsupported stage: {stage!r}")
    if not isinstance(patch.get("items"), list):
        raise SystemExit("Patch must contain an items array")

    structural, beats = collect_targets(data)
    target_group, field_name, anchors = STAGES[stage]
    expected = structural if target_group == "structural" else beats
    items: dict[str, dict[str, Any]] = {}
    for item in patch["items"]:
        target_id = item.get("target_id")
        if not isinstance(target_id, str) or target_id in items:
            raise SystemExit(f"Missing or duplicate target_id: {target_id!r}")
        if field_name not in item:
            raise SystemExit(f"{target_id}: missing {field_name!r}")
        items[target_id] = item
    missing = [target for target in expected if target not in items]
    extra = [target for target in items if target not in set(expected)]
    if missing or extra:
        raise SystemExit(f"Target coverage mismatch; missing={missing}, extra={extra}")

    root = JsonPositions(text).parse()
    objects: dict[str, Node] = {}
    for obj in walk_objects(root):
        id_member = obj.member("id")
        if id_member and isinstance(id_member.value.scalar, str):
            target_id = id_member.value.scalar
            if target_id in objects:
                raise SystemExit(f"Duplicate id in working JSON: {target_id}")
            objects[target_id] = obj

    operations: list[tuple[int, str]] = []
    for target_id in expected:
        obj = objects.get(target_id)
        if obj is None:
            raise SystemExit(f"Cannot locate object for {target_id}")
        if obj.member(field_name) is not None:
            raise SystemExit(f"{target_id}: field {field_name!r} already exists")
        anchor = next((obj.member(name) for name in anchors if obj.member(name) is not None), None)
        if anchor is None:
            raise SystemExit(f"{target_id}: cannot find insertion anchor from {anchors}")
        operations.append(insertion_text(text, obj, anchor, field_name, items[target_id][field_name]))

    output_text = text
    for offset, addition in sorted(operations, reverse=True):
        output_text = output_text[:offset] + addition + output_text[offset:]
    json.loads(output_text)

    output = args.output or args.working_json
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(output_text.encode("utf-8"))
    print(f"Applied {stage} to {len(expected)} targets: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
