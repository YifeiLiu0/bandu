# Review guidelines: dimensions, severity, scoring

## Reviewer stance

Judge only the final reader-facing text against the source. Every finding must name one concrete defect at one concrete location, carry verbatim evidence, and end with an executable fix. Style preference without a reader cost is not a finding.

## Severity levels

- `blocker`: the text must not ship — it misleads the reader about the source or destroys a later payoff.
- `major`: revise before shipping — a real reader cost, but the item still functions.
- `minor`: polish — small friction, safe to ship.

## Dimension 1: accuracy (准确性)

The commentary must not fabricate facts or deviate from the source.

Check each commentary text against its own node's source:

- fabricated fact, number, name, quote, or capability the source never states — `blocker`;
- inverted or contradicted source claim — `blocker`;
- overstated certainty or scope (source says "may/often", commentary says "always/must") — `major`;
- unsupported generalization beyond the source's stated boundary — `major`;
- analogy detail phrased so it reads as a book claim — `major`;
- imprecise but harmless wording — `minor`.

Evidence: the commentary quote plus at least one verbatim source quote that contradicts it or whose absence of support is being asserted (quote the nearest passage the claim should have come from).

## Dimension 2: consistency (一致性)

No recurring near-identical delivery, no re-explaining, no premature explanation.

Maintain three ledgers over the whole chapter in item order:

- **Form ledger** — presentation form, opening pattern, device, roast target per text. Flag: three or more consecutive texts with the same presentation form (`major`, chapter-scope pattern finding); two texts whose structure or joke is near-duplicate (`major`) — seed candidates from the precheck's `duplicate_pairs` and `repeated_openings`, then verify by reading both texts.
- **Concept ledger** — concept → the item that first explains it. Flag a later text that re-explains the same concept instead of reusing it (`major`; a one-clause reminder is `minor`).
- **Horizon ledger** — the reader's current position. Flag commentary that explains content whose source location is later than the current beat: revealing a later unit's answer or punchline — `blocker`; merely front-loading an explanation the book gives later — `major`. Verify by locating the later beat whose `source_markdown` actually covers it.

Evidence: quote both occurrences — the current text (`commentary_quote`) and the earlier explanation (a `source_refs` entry with `"quote_from": "commentary"`) or the later source passage (`"quote_from": "source"`).

## Dimension 3: simplicity (简易性)

The commentary must significantly lower the comprehension barrier.

Test sentence per text: 一个零背景读者能否只靠这条评论跨过这个理解台阶？

- jargon used on first appearance without an inline plain-language explanation, blocking comprehension — `major`;
- the explanation is harder to parse than the source passage it explains — `major`;
- abstract-noun chains, stacked qualifiers, or sentences doing three jobs at once — `minor` (`major` when the payoff becomes unrecoverable);
- an analogy longer than the point it serves, or requiring its own explanation — `minor`.

Evidence: the commentary quote alone suffices; add a source quote when claiming "harder than the source".

## Dimension 4: fun (趣味性)

The commentary should make the book pull like a short drama or game: visible stakes, fast payoffs, humor that lands.

- a hook that promises a payoff the unit's own content cannot deliver (the fact is true but the tease oversells) — `major`;
- generic cliffhanger phrasing ("精彩的还在后面"-type) with no named question — `major`;
- quiz or teacherly tone where a companion voice was expected — `minor` to `major` by reach;
- a joke that requires background knowledge the target reader lacks — `minor`;
- five or more consecutive items delivering no reward (no new understanding, no landed joke, no answered question) — `major`, chapter-scope pattern finding;
- a closing question that neither can be answered from the unit nor names what the next unit resolves — `minor`.

Anti-noise rules: a roast being sarcastic is the voice contract, not a defect; humor density is not scored per item — only absent or failed reward is. Fun findings are never `blocker`; blockers are reserved for accuracy and spoiler damage.

## Evidence rules

- Every quote is a verbatim substring of the text it cites, at most 120 characters, and the smallest span that proves the issue.
- One finding per concrete occurrence. Systemic repetition becomes one chapter-scope pattern finding with `related_target_ids` instead of N copies.
- Precheck statistics are leads, never evidence: verify by reading the texts before filing.

## Scores

Per chapter, per dimension, an integer 0–10. Hard caps from that chapter's findings in the dimension (validator-enforced):

| Findings present | Cap / floor |
| --- | --- |
| any blocker | score ≤ 4 |
| else any major | score ≤ 7 |
| else any minor | score ≤ 9 |
| none | score ≥ 8 |

Within the allowed band, anchor on: 10 exemplary; 8–9 ship as-is; 5–7 revise the findings, then ship; 0–4 rework the dimension. Write one-sentence `rationale` per dimension naming what dominated the score.

Verdict: any blocker anywhere → `rework`; else any major → `revise`; else `pass`.
