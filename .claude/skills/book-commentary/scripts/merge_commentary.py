#!/usr/bin/env python3
"""Merge legacy unit/beat comment artifacts into one final-only commentary JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_bytes().decode("utf-8"))


def source_sequence(source: dict[str, Any]):
    sequence: list[tuple[str, str, bool]] = []
    book = source["book"]
    sequence.append((book["id"], "book", book.get("plan") is not None))
    for chapter in book["chapters"]:
        sequence.append((chapter["id"], "chapter", chapter.get("plan") is not None))
        for section in chapter["sections"]:
            sequence.append((section["id"], "section", section.get("plan") is not None))
            for beat in section.get("beats", []):
                sequence.append((beat["id"], "beat", True))
            for subsection in section.get("subsections", []):
                sequence.append((subsection["id"], "subsection", subsection.get("plan") is not None))
                for beat in subsection.get("beats", []):
                    sequence.append((beat["id"], "beat", True))
    return sequence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="pre-analysis enriched segmentation JSON")
    parser.add_argument("unit_comments", type=Path, help="legacy unit_comments artifact")
    parser.add_argument("beat_comments", type=Path, help="legacy beat_comments artifact")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = load(args.source)
    unit_artifact = load(args.unit_comments)
    beat_artifact = load(args.beat_comments)
    if unit_artifact.get("stage") != "unit_comments" or beat_artifact.get("stage") != "beat_comments":
        raise SystemExit("Expected unit_comments and beat_comments input artifacts")
    if unit_artifact.get("settings") != beat_artifact.get("settings"):
        raise SystemExit("Input artifact settings differ")
    units = {item["target_id"]: item for item in unit_artifact["items"]}
    beats = {item["target_id"]: item for item in beat_artifact["items"]}
    items: list[dict[str, Any]] = []
    for target_id, unit_type, eligible in source_sequence(source):
        if unit_type != "beat":
            if not eligible:
                continue
            source_item = units[target_id]
            items.append({
                "target_id": target_id,
                "unit_type": unit_type,
                "commentary": source_item["commentary"],
            })
            continue
        source_item = beats[target_id]
        items.append({
            "target_id": target_id,
            "unit_type": "beat",
            "commentaries": [
                {
                    "voice": comment["voice"],
                    "comment_type": comment["comment_type"],
                    "presentation_form": comment["presentation_form"],
                    "text": comment["text"],
                }
                for comment in source_item["commentaries"]
            ],
        })

    output = {
        "status": "ok",
        "schema_version": "0.7.0",
        "stage": "book_commentary",
        "source": {
            "document_id": source.get("document_id"),
            "source_path": source.get("source_path"),
            "source_sha256": source.get("source_sha256"),
        },
        "settings": unit_artifact["settings"],
        "items": items,
        "validation": {"errors": [], "warnings": []},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(f"Merged {len(items)} final-comment items: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
