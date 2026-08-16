---
name: z-grounded-source-qa
description: >-
  Use this skill whenever the user wants answers, summaries, comparisons,
  decisions, quotations, persona simulations, articles, scripts, or claim
  checks that must stay grounded in user-provided local source files. Trigger
  for source-grounded QA, evidence-based answering, corpus questions, transcript
  analysis, “只根据这些资料回答”, “按原文核对”, “给出页码/时间戳/出处”, “不要编”,
  “从访谈里找依据”, and reusable question answering over Markdown or text
  corpora. Run multi-expression retrieval, preserve source locations, separate
  supported claims from inference, and retry retrieval before declaring that a
  source is silent.
---
> **EN:** Grounded QA over local materials: answer questions based strictly on the provided documents/sources.
>

# Grounded Source QA

Turn arbitrary local Markdown or text files into a traceable evidence base for answering, synthesis, comparison, writing, and persona simulation.

The Skill carries the workflow and retrieval engine. The user's corpus stays outside the Skill.

## Start with the source contract

Identify the exact files or directories the user placed in scope.

- Accept Markdown, plain text, transcripts, meeting notes, exported web pages, and parsed documents
- Convert PDF, Office, images, audio, or video to Markdown/text with an appropriate parser before retrieval
- Keep the original files unchanged
- Do not silently add web knowledge, model memory, or unrelated workspace files
- State any source-access limitation that materially affects the answer

Read [references/source-preparation.md](references/source-preparation.md) when the corpus needs conversion, page markers, transcript metadata, or cleanup.

## Retrieval workflow

Run this workflow before making material claims from the corpus:

1. Restate the user's question as a claim or decision to resolve
2. Generate 3–8 retrieval expressions covering:
   - the user's wording
   - synonyms and abbreviations
   - likely source wording
   - causes, mechanisms, risks, or counterarguments needed for a complete answer
3. Run the deterministic retrieval script:

   ```bash
   python3 scripts/search_evidence.py \
     --source "/path/to/source-or-directory" \
     --query "core phrase" \
     --query "synonym" \
     --query "likely source wording" \
     --top-k 8 \
     --format json
   ```

4. Inspect the evidence objects for coverage, location, and context
5. Map each intended claim to evidence
6. If the evidence covers only part of the question, change the expressions and run a second retrieval
7. Read the closest source sections directly when results are fragmented, conflicting, or low-confidence
8. Draft only after the evidence set is sufficient

Increasing `--top-k` alone is not a second retrieval. Change the wording or search a missing mechanism, exception, time period, or opposing view.

One empty query means the current expressions missed. It does not establish that the corpus lacks relevant material.

## Evidence discipline

Classify each material statement internally:

1. **Direct:** Explicitly stated in one source passage
2. **Synthesis:** Supported by multiple passages combined without adding a new premise
3. **Inference:** A reasonable conclusion that depends on an assumption; label the assumption
4. **Unsupported:** No adequate evidence after a second retrieval and direct reading; omit it or state the gap

For high-stakes, disputed, public, or publication-bound claims, read [references/evidence-contract.md](references/evidence-contract.md) and preserve the evidence IDs used.

When sources conflict:

- show the conflicting statements and locations
- distinguish date, scope, speaker, and definition differences
- avoid silently choosing the more convenient passage

## Answer modes

Choose the smallest mode that satisfies the user.

### Natural answer

Lead with the answer. Add compact source locations after the claims they support.

### Evidence audit

Use when the user asks for verification, citations, an audit trail, or publication review:

```markdown
## Conclusion

## Evidence
- Claim — source file:line, page/time when available

## Inferences and assumptions

## Gaps or conflicts
```

### Persona or voice simulation

Use source-backed reasoning and vocabulary. Preserve qualifiers and uncertainty. Mark extrapolation when the source supplies a framework but no direct answer. Never present invented private thoughts as source material.

## Retrieval output

`scripts/search_evidence.py` uses only the Python standard library and:

- recursively discovers `.md`, `.markdown`, and `.txt` files
- returns complete semantic paragraphs
- keeps document, line, page, timestamp, section, and speaker metadata
- ranks multi-expression coverage
- merges adjacent matched paragraphs
- deduplicates repeated content while retaining additional locations
- supports explicit regular-expression queries with `--regex`
- returns JSON evidence objects for reliable downstream use

The script exits with code `1` when no evidence matches, while still emitting a valid result and a query-miss warning.

## Create a dedicated Skill from this base

Use a dedicated Skill when the same person, book, policy, project, or product corpus will be queried repeatedly. The specialization should combine four layers:

```text
retrieval capability + bounded corpus + answer contract + eval questions
```

Prepare page-marked Markdown from `pdftotext` output when needed:

```bash
python3 scripts/prepare_pdftotext.py \
  extracted.txt prepared-source.md \
  --title "Source title"
```

Generate a self-contained specialization:

```bash
python3 scripts/create_specialized_skill.py \
  --name z-example-advisor \
  --title "Example Advisor" \
  --mode advisor \
  --source prepared-source.md \
  --output-root /path/to/.agent/skills \
  --trigger "example book" \
  --question "What should I do first and why"
```

Choose `persona`, `advisor`, `policy`, or `source-qa` according to the intended answer contract. The generated Skill includes its own retriever, corpus directory, source hashes, profile, and eval questions.

Read [references/specialization-guide.md](references/specialization-guide.md) before public release or when the specialization needs custom voice, policy authority, source reliability, or failure-boundary rules.

## Completion check

Before sending the final answer, confirm:

- every material claim maps to direct evidence, synthesis, or a labeled inference
- at least one multi-expression retrieval ran
- incomplete first-round evidence triggered a rewritten second retrieval
- query miss and source absence were kept separate
- conflicts and source limitations are visible
- source locations are precise enough for another person to verify
- the final format matches the user's requested answer, audit, article, or simulation
- a generated specialization was tested with realistic questions before being shared
