---
name: robustness-checker
description: Design and run risk-targeted robustness, sensitivity, error, and baseline checks for an approved mathematical model, emitting compact machine evidence in lean mode and a final report in submission mode.
---

# Purpose

Test the claims most likely to fail. Choose checks from the model's assumptions and decision risks rather than filling a generic checklist.

# Preconditions

- Approved main and usable baseline executed.
- Run summary, method card, probe summary, and relevant outputs exist.
- Claim or decision to be tested is known.

# Workflow

1. Identify load-bearing assumptions and claims.
2. Select applicable checks:
   - parameter or weight perturbation;
   - alternate split or resampling;
   - seed stability;
   - outlier/missing-data treatment;
   - constraint/capacity perturbation;
   - baseline comparison;
   - output concentration/rank stability;
   - error and uncertainty analysis.
3. State perturbation ranges and why they are meaningful before interpreting results.
4. Run checks with fixed seeds where stochastic.
5. Save compact metrics to:

`robustness/Qx/qx_robustness_summary.json`

6. In `submission`, also save:

`robustness/Qx/qx_robustness_report.md`

7. If the stability verdict affects method continuation or claim scope, invoke one choice card and log the human answer in `qx_decisions.jsonl`.

# Constraint Closure Audit

When the model declares hard constraints, do not trust the optimizer's own `constraints_ok` field. Recompute every constraint from the final result file:

1. Write or reuse a small audit script that reads the saved results at full precision and prints only conclusions (`PASS`/`FAIL`, violation count, max error, and at most five violation locations).
2. Audit every comparison baseline as well: auto-discover keys whose names suggest `baseline`, `naive`, `greedy`, `就近`, `等权`, `不调整`, or `lower_bound`; each must be audited or the audit fails.
3. Two legal outcomes for a baseline: it satisfies all hard constraints, or it violates one and is explicitly labeled in the report as infeasible/theoretical lower bound only.
4. Record the credential in the robustness summary or result report:

```text
<!-- AUDIT_OK source=results.json rechecked_at=<timestamp> n_constraints=N -->
```

5. If no hard constraints exist, record `n_constraints=0` with a one-line statement instead of skipping the credential.

# Summary Contract

Record:

- tested claim/assumption;
- input and result source paths;
- perturbation;
- metric and threshold if predeclared;
- observed value;
- status `PASS`, `CONDITIONAL`, or `FAIL`;
- limitation;
- fallback-trigger relevance;
- constraint-recheck status and credential, when constraints exist.

# Rules

- Do not run irrelevant checks merely to reach a count.
- Do not invent a threshold after seeing the result without labeling it exploratory.
- Do not convert stability metrics into the human confidence verdict.
- Do not create `robustness-checker_modeler_decision.md`.
- A failed robustness check is evidence for adjust/fallback/claim downgrade, not permission for AI to decide.
- Do not label a constraint-violating baseline as feasible; state it as a theoretical bound or fix it.

# Verification

- Every major final claim has a supporting check or explicit limitation.
- Perturbations are justified and reproducible.
- Baseline and main comparisons remain metric-compatible.
- Concentration/degeneracy risks are revisited when relevant.
- Submission report sources its numbers from the summary and experiment artifacts.
- Hard constraints are re-audited from final results, including baselines, with a credential.
