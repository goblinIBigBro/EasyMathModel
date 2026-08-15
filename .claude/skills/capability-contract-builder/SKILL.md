---
name: capability-contract-builder
description: Turn parsed problem requirements into a question-type-agnostic capability checklist with falsifiable acceptance criteria, so modeling, code review, and paper writing verify that every required capability was actually delivered instead of quietly simplified.
---

# Purpose

Convert "what the problem asks for" into machine-checkable acceptance items. The checklist is the cross-stage contract: modeling claims each capability, code implements it with a runtime assertion where possible, reviewers verify it, and the paper may only claim capabilities that passed.

# Preconditions

- `planning/parse/problem_parse.json` and `planning/classification/problem_classification.json` exist.
- Problem text or OCR-extracted text is available for sentence anchoring.

# When to Use

Build the checklist when the problem has multiple verifiable capabilities or is parameter-dense (roughly 20+ quantified conditions). A pure descriptive or single-mechanism question may skip it; record the skip reason in the manifest instead of creating an empty file.

# Inputs

- problem parse and classification;
- problem statement text (prefer OCR text over raw PDF);
- ambiguity/framing decisions already logged by the human.

# Workflow

1. Read the parse and classify every decision/goal/mechanism sentence as a candidate capability.
2. For each subquestion, list the capabilities the problem explicitly requires — not the approach you intend to take.
3. For each capability record:
   - `id`: `Qx-Cn`;
   - `subquestion`;
   - `name`;
   - `judge`: `machine` (a deterministic gate can check it) or `semantic` (needs human/LLM judgment);
   - `criterion`: what "delivered" means;
   - `required_output`: path of the deliverable, when applicable;
   - `machine_check`: `delivery`, `ingest`, `constraint`, `facts`, or `leakage`, when applicable;
   - `falsifiable_check`: one sentence stating how code would prove the capability and what would disprove it;
   - `source_sentence`: the original problem sentence ID (S1, S2, ...) that requires this capability.
4. Anchor every decision/goal/mechanism sentence to at least one capability. Unanchored sentences are an error.
5. For semantic or ambiguous capabilities, do not silently settle the meaning; route the interpretation choice to the human framing card.
6. Save `planning/capability_checklist.json`.

# Contract

```json
{
  "schema_version": 1,
  "problem_id": "2026A",
  "n_subproblems": 4,
  "capabilities": [
    {
      "id": "Q1-C1",
      "subquestion": "Q1",
      "name": "five-tuple event extraction",
      "judge": "machine",
      "criterion": "every output record contains subject/event/object/time/location and none are empty",
      "required_output": "output/events.json",
      "machine_check": "delivery",
      "falsifiable_check": "extraction outputs carry span positions and the extractor is not a str.find dictionary matcher; otherwise the capability is not met",
      "source_sentence": "S2"
    },
    {
      "id": "Q2-C1",
      "subquestion": "Q2",
      "name": "hard constraints in solver",
      "judge": "machine",
      "criterion": "the declared capacity/budget/time-window constraints are part of the optimization model",
      "machine_check": "constraint",
      "falsifiable_check": "constraints are declared inside the solver model (not post-hoc patching) and the final solution satisfies all of them; any violation means not met",
      "source_sentence": "S7"
    }
  ]
}
```

# Rules

- Write what the problem requires, not what you plan to build. "Classify" must not be written when the problem requires extraction.
- Do not degrade a capability into a proxy (file-id labels, string matching for semantics, same-data derived features predicting derived labels).
- Every subquestion has at least one capability; an undeliverable subquestion cannot be hidden.
- Semantic and non-delivery machine capabilities require `falsifiable_check`.
- Do not invent sentences or renumber the problem text.
- Do not create this checklist as decoration; downstream skills consume it only when present.

# Verification

- Every capability traces to a source sentence.
- Every decision/goal/mechanism sentence is claimed by at least one capability.
- `falsifiable_check` is concrete enough that code can fail it.
- No method choice leaked into the checklist.

# Downstream Use

- `model-assumptions-builder` and `method-selector`: map capability IDs in the method card.
- `model-code-analyzer`: plan `validate_capability()` assertions from `falsifiable_check`.
- `python-code-reviewer` / `matlab-code-reviewer`: add the `capability_contract` check when the checklist exists.
- `paper-section-writer` and `output-standards-auditor`: paper may claim only capabilities that passed.
