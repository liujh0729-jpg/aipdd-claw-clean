# Evidence contract

Use this contract when the answer will support a public claim, a high-stakes decision, a disputed interpretation, or a formal audit.

## Evidence object

Each retrieved result should retain:

- `evidence_id`: stable content-derived identifier
- `matched_terms`: expressions that matched
- `score`: deterministic retrieval score
- `content`: complete semantic paragraph
- `location.document`: source document
- `location.line_start` and `line_end`: local verification range
- `location.page`: page marker when present
- `location.timestamp`: transcript time when present
- `location.section`: Markdown heading path
- `location.speaker`: parsed speaker when present
- `additional_locations`: duplicate occurrences in other documents
- `previous_context` and `next_context`: short neighboring previews
- `content_hash`: deduplication key

## Claim mapping

For each material claim, keep an internal record:

| Claim | Evidence IDs | Level | Assumption | Conflict |
| --- | --- | --- | --- | --- |
| Proposed conclusion | ev-... | Direct / Synthesis / Inference | Any added premise | Conflicting evidence ID |

## Levels

### Direct

The source explicitly supports the claim. Preserve qualifiers, scope, speaker, and date.

### Synthesis

Two or more passages jointly support the claim. Do not add a premise that the sources do not supply.

### Inference

The conclusion depends on an additional assumption. State that assumption and keep the language proportional to uncertainty.

### Unsupported

Evidence remains inadequate after rewritten retrieval and direct reading. Remove the claim or state the gap.

## Conflict handling

When sources disagree:

1. compare dates
2. compare definitions
3. compare speakers and authority
4. compare scope and exceptions
5. show both locations
6. state what additional evidence would resolve the conflict

## Citation compactness

For normal answers, cite only the locations needed to verify the claim.

For audits, include evidence IDs and precise locations.

Examples:

```text
product-interview.md:42, PDF page 7, 00:12:34
```

```text
policy-v2.md:88-93
```
