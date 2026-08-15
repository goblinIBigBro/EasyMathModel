---
name: python-code-reviewer
description: Review, run, debug, and verify approved Python modeling code against its code plan, data contract, method decision, risk conditions, and experiment outputs, saving one compact JSON review.
---

# Preconditions

- Python code and `code/Qx/qx_code_plan.md` exist.
- Approved method decision, method card, data profile, and relevant run summary are available.
- Required inputs are accessible.

# Workflow

1. Resolve the approved main and usable baseline. Flag scripts for unapproved candidates unless a fallback activation exists.
2. Inspect and run the code in the intended order.
3. Evaluate required checks:
   - `syntax`: imports, execution, exceptions, and obvious runtime faults.
   - `input_contract`: paths, fields, units, shapes, missing-data handling, and raw-data protection.
   - `method_alignment`: formulas, objectives, constraints, assumptions, main/baseline roles, and fallback scope match the approved plan.
   - `reproducibility`: seed, deterministic setup, dependency/runtime record, and rerun consistency.
   - `output_contract`: saved tables/metrics/figures, valid run summary, comparable main/baseline metrics, degeneracy evidence, and fallback-trigger state.
4. When `planning/capability_checklist.json` exists, add the `capability_contract` check: every capability's `falsifiable_check` has a runtime assertion or equivalent executable evidence; no proxy labels (file IDs, filenames, row indices), no string matching standing in for semantic capabilities, no scoring without the claimed downstream action.
5. Add risk-specific checks only when relevant, such as leakage, constraint feasibility, numerical stability, or scale.
6. If asked to fix findings, make minimal changes, rerun affected checks, and record the repair. Otherwise report findings without changing code.
7. Save `code/Qx/reviews/qx_python_review.json`.

# Review Schema

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "language": "python",
  "reviewed_files": [],
  "decision_id": "q1_method_choice",
  "checks": {
    "syntax": {"status": "PASS", "evidence": []},
    "input_contract": {"status": "PASS", "evidence": []},
    "method_alignment": {"status": "PASS", "evidence": []},
    "reproducibility": {"status": "PASS", "evidence": []},
    "output_contract": {"status": "PASS", "evidence": []},
    "capability_contract": {"status": "NOT_APPLICABLE", "evidence": []}
  },
  "findings": [],
  "verdict": "PASSED",
  "reviewed_at": "ISO-8601"
}
```

Statuses are `PASS`, `FAIL`, or `NOT_APPLICABLE` with a reason. Any required `FAIL` blocks G3.

# Rules

- Do not pad evidence to reach a count.
- Do not fabricate execution or outputs.
- Do not approve a toy diagnostic reference as the official baseline.
- Do not silently change mathematical meaning.
- Do not create success logs beyond the review JSON.
- Treat code newer than its review as requiring the affected checks to rerun, not necessarily the entire pipeline.
- Do not mark `capability_contract` as PASS when a falsifiable check lacks executable evidence.
- Do not delete or weaken a runtime capability assertion to make the check pass.

# Verification

- Every required named check has concrete evidence.
- When the checklist exists, capability assertions cover every falsifiable check and fail loudly on proxies.
- Main and baseline are approved and comparable.
- Run summary and on-disk outputs agree.
- Review verdict follows check statuses.
