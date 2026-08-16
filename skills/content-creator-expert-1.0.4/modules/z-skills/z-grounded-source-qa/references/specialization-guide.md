# Specialization guide

Use this guide when turning the generic retrieval capability into a dedicated person, book, policy, project, product, or team Skill.

## The four-layer formula

```text
specialized Skill = retrieval capability + bounded corpus + answer contract + eval questions
```

The retrieval capability gives every specialization the same evidence discipline. The other three layers determine whether it feels useful in a real situation.

## Pick a mode

### Persona

Use for public talks, interviews, essays, or other material associated with one person.

- Default to natural first-person simulation
- Keep private thoughts and later events out of scope
- Mark framework extrapolation once and briefly
- Add source-audit questions that force the Skill to show pages or sections

### Advisor

Use for books, courses, research collections, or a curated school of thought.

- Extract the source framework before applying it
- Separate author intent from application to the user's situation
- End with a small action when the user asks for guidance
- Avoid turning a contextual opinion into a universal law

### Policy

Use for reimbursement, travel, leave, procurement, benefits, onboarding, customer support, and other operating rules.

- Lead with eligible, ineligible, conditional, or insufficient evidence
- Surface documents, limits, deadlines, exceptions, and approval authority
- Compare version dates when rules conflict
- Treat the result as pre-check guidance, not final approval

### Source QA

Use for project archives, meeting notes, research, customer interviews, product documentation, and mixed corpora.

- Choose natural answers, evidence audits, comparisons, or publication fact-checks as needed
- Keep every material claim tied to a location

## Build a self-contained Skill

Prepare PDF text first when necessary:

```bash
pdftotext -layout source.pdf extracted.txt

python3 scripts/prepare_pdftotext.py \
  extracted.txt prepared-source.md \
  --title "Source title"
```

For numbered quotation collections, add `--mode numbered`.

Generate the specialization:

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

The generated directory contains:

```text
z-example-advisor/
├── MODULE.md
├── README.md
├── scripts/search_evidence.py
├── references/profile.md
├── references/source-manifest.json
├── references/corpus/
└── evals/evals.json
```

## Customize for quality

1. Edit `references/profile.md` so the role, tone, source reliability, and forbidden claims are explicit
2. Clean the corpus into complete semantic paragraphs and preserve page or section markers
3. Add 3–8 realistic questions, including one source-audit question and one source-gap question
4. Run multi-expression retrieval for every example
5. Review whether the answer sounds natural while keeping inference visible
6. Add a topic index or golden answers only when repeated tests show they improve consistency

The generator provides a working starting point. Corpus quality, question design, answer boundaries, and continued evaluation determine the final ceiling.
