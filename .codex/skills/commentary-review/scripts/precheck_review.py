#!/usr/bin/env python3
"""Deterministic advisory statistics over one final commentary artifact.

Prints a JSON stats block (form runs, near-duplicate text pairs, repeated
openings, length stats, term first mentions) used as leads by the model
review. Emits no judgments and no findings.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_bytes().decode("utf-8"))


def collect_texts(commentary: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten every commentary text in item order with its address."""
    texts: list[dict[str, Any]] = []
    for item in commentary["items"]:
        target_id = item["target_id"]
        if item["unit_type"] == "beat":
            for index, comment in enumerate(item["commentaries"]):
                texts.append({
                    "target_id": target_id,
                    "kind": "beat_commentary",
                    "index": index,
                    "voice": comment["voice"],
                    "presentation_form": comment["presentation_form"],
                    "text": comment["text"],
                })
        else:
            opening = item["commentary"]["opening_hook"]
            closing = item["commentary"]["closing_question"]
            texts.append({
                "target_id": target_id,
                "kind": "opening_hook",
                "index": None,
                "voice": opening["voice"],
                "presentation_form": opening["presentation_form"],
                "text": opening["text"],
            })
            texts.append({
                "target_id": target_id,
                "kind": "closing_question",
                "index": None,
                "voice": closing["voice"],
                "presentation_form": None,
                "text": closing["text"],
            })
    return texts


def address(entry: dict[str, Any]) -> str:
    if entry["kind"] == "beat_commentary":
        return f"{entry['target_id']}#{entry['index']}:{entry['voice']}"
    return f"{entry['target_id']}#{entry['kind']}"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\s\W_]+", "", text, flags=re.UNICODE)


def char_ngrams(text: str, n: int) -> set[str]:
    normalized = normalize(text)
    if len(normalized) < n:
        return {normalized} if normalized else set()
    return {normalized[i:i + n] for i in range(len(normalized) - n + 1)}


def form_stats(texts: list[dict[str, Any]]) -> tuple[dict[str, int], dict[str, Any]]:
    forms = [t["presentation_form"] for t in texts if t["presentation_form"]]
    counts = dict(Counter(forms).most_common())
    sequence = [(address(t), t["presentation_form"]) for t in texts if t["presentation_form"]]
    best = {"form": None, "length": 0, "addresses": []}
    run: list[tuple[str, str]] = []
    for addr, form in sequence + [("", "")]:
        if run and form == run[-1][1]:
            run.append((addr, form))
        else:
            if len(run) > best["length"]:
                best = {"form": run[-1][1], "length": len(run), "addresses": [a for a, _ in run]}
            run = [(addr, form)]
    return counts, best


def duplicate_pairs(texts: list[dict[str, Any]], ngram: int, threshold: float) -> list[dict[str, Any]]:
    grams = [char_ngrams(t["text"], ngram) for t in texts]
    pairs = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if not grams[i] or not grams[j]:
                continue
            union = len(grams[i] | grams[j])
            similarity = len(grams[i] & grams[j]) / union if union else 0.0
            if similarity >= threshold:
                pairs.append({
                    "a": address(texts[i]),
                    "b": address(texts[j]),
                    "jaccard": round(similarity, 3),
                })
    return sorted(pairs, key=lambda p: -p["jaccard"])


def repeated_openings(texts: list[dict[str, Any]], prefix_len: int, min_count: int) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for entry in texts:
        prefix = normalize(entry["text"])[:prefix_len]
        if prefix:
            buckets[prefix].append(address(entry))
    return [
        {"prefix": prefix, "count": len(addresses), "addresses": addresses}
        for prefix, addresses in sorted(buckets.items(), key=lambda kv: -len(kv[1]))
        if len(addresses) >= min_count
    ]


def length_stats(texts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for entry in texts:
        groups[f"{entry['kind']}:{entry['voice']}"].append(len(entry["text"]))
    return {
        key: {
            "count": len(lengths),
            "min": min(lengths),
            "mean": round(statistics.mean(lengths), 1),
            "max": max(lengths),
        }
        for key, lengths in sorted(groups.items())
    }


def term_first_mention(texts: list[dict[str, Any]], min_texts: int, top: int) -> list[dict[str, Any]]:
    """Latin words and CJK bigrams appearing in >= min_texts texts, with first location."""
    presence: dict[str, list[str]] = defaultdict(list)
    for entry in texts:
        tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", entry["text"]))
        han = re.findall(r"[一-鿿]{2,}", entry["text"])
        for chunk in han:
            tokens.update(chunk[i:i + 2] for i in range(len(chunk) - 1))
        for token in tokens:
            presence[token.lower() if token.isascii() else token].append(address(entry))
    rows = [
        {"term": term, "texts": len(addresses), "first": addresses[0]}
        for term, addresses in presence.items()
        if len(addresses) >= min_texts
    ]
    return sorted(rows, key=lambda r: (-r["texts"], r["term"]))[:top]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("segmentation", type=Path, help="original segmentation JSON (unused for stats; kept for a uniform CLI)")
    parser.add_argument("commentary", type=Path, help="final commentary JSON")
    parser.add_argument("--ngram", type=int, default=8)
    parser.add_argument("--jaccard", type=float, default=0.35)
    parser.add_argument("--prefix-len", type=int, default=10)
    parser.add_argument("--min-prefix-count", type=int, default=3)
    parser.add_argument("--min-term-texts", type=int, default=3)
    parser.add_argument("--top-terms", type=int, default=50)
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()

    commentary = load_json(args.commentary)
    texts = collect_texts(commentary)
    form_counts, max_form_run = form_stats(texts)
    stats = {
        "texts_indexed": len(texts),
        "form_counts": form_counts,
        "max_form_run": max_form_run,
        "duplicate_pairs": duplicate_pairs(texts, args.ngram, args.jaccard),
        "repeated_openings": repeated_openings(texts, args.prefix_len, args.min_prefix_count),
        "length_stats": length_stats(texts),
        "term_first_mention": term_first_mention(texts, args.min_term_texts, args.top_terms),
    }
    payload = json.dumps(stats, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
