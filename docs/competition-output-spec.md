# Competition Output Specification

> The packaged output contract for math-modeling contests. It converts "the paper must be honest and complete" into checkable rules across the pipeline: capability acceptance, modeling assumptions, code and results, figures, and final paper compliance.
>
> Companion skills: `capability-contract-builder`, `output-standards-auditor`, plus hardened rules in `model-assumptions-builder`, `figure-table-planner`, `robustness-checker`, `model-code-analyzer`, and both code reviewers.

## 1. Purpose

Contest teams fail most often on workflow defects, not on missing models:

- the problem asks for X, the team builds Y;
- a number in the paper is produced by no script in the repo;
- a bug is fixed late, but the paper still carries the old numbers;
- figures are planned but never generated, or generated but never embedded;
- the abstract was written before the results existed, so it invents values.

This specification exists so each of those failures is mechanically detectable. It never decides a modeling judgment; it only makes the evidence required for a claim explicit and checkable.

## 2. Workspace Artifact Contract

Use one canonical path per artifact. A file that exists twice invites version drift.

| Stage | Artifact | Minimum | Consumers |
|---|---|---|---|
| Parse | `planning/parse/problem_parse.json` | structural | classifier, assumptions, method card |
| Classify | `planning/classification/problem_classification.json` | structural | capability contract, method selector |
| Capability contract (optional) | `planning/capability_checklist.json` | structural | assumptions, code plan, reviewers, paper |
| Symbols | `planning/symbol_table.md` | non-empty | every modeling/writing step |
| Assumptions | `planning/model_assumptions.md` | non-empty | method card, probes, robustness |
| Method | `methods/Qx/qx_method_card.md` | non-empty | code plan, reviews, writer |
| Decision ledger | `methods/Qx/qx_decisions.jsonl` | append-only | every gate |
| Risk probe | `methods/Qx/probes/risk_probe_summary.json` | 7 fields | G2 |
| Code plan | `code/Qx/qx_code_plan.md` or `code/matlab/Qx/...` | non-empty | generators, reviewers |
| Review | `code/Qx/reviews/qx_<lang>_review.json` | 5 named checks (+optional `capability_contract`) | G3 |
| Run | `results/Qx/experiments/roundN/run_summary.json` | non-empty | result report, robustness, writer |
| Robustness | `robustness/Qx/qx_robustness_summary.json` | non-empty | G4 |
| Freeze | `results/Qx/reports/frozen_numbers.json` | immutable | writer, all audits |
| Paper | `paper/main.tex` + `paper/sections/*.tex` | main ≥ 5 KB, sections ≥ 3 | compile, audits |
| Output audit | `paper/audits/output_spec_report.md` | named checks | G6 pre-flight |

Naming rules that prevent silent failures:

- figure IDs start with `fig_` or `tikz_`; names without a prefix are invisible to reconciliation;
- per-subquestion results are `figures/problem_N_results.json`, aggregated as `figures/all_results.json`;
- stale versions (`results_v1.json`, `results_old.json`) are removed, never kept beside the current file;
- `data_raw/` is read-only; cleaned data lives in `data_clean/`.

## 3. Capability Contract

For parameter-dense problems (roughly 20+ quantified conditions) or problems with multiple verifiable capabilities, build `planning/capability_checklist.json`:

```json
{
  "schema_version": 1,
  "problem_id": "2026A",
  "n_subproblems": 4,
  "capabilities": [
    {
      "id": "Q2-C1",
      "subquestion": "Q2",
      "name": "hard constraints in solver",
      "judge": "machine",
      "criterion": "declared capacity/budget/time-window constraints are part of the optimization model",
      "machine_check": "constraint",
      "falsifiable_check": "constraints are declared inside the solver model (not post-hoc patching) and the final solution satisfies all of them; any violation means not met",
      "source_sentence": "S7"
    }
  ]
}
```

Rules:

- write what the problem requires, not what you plan to build;
- `judge` is `machine` when a deterministic gate can verify it, otherwise `semantic`;
- every semantic and non-delivery machine capability needs a `falsifiable_check` that code can actually fail;
- every decision/goal/mechanism sentence in the problem anchors to at least one capability (`source_sentence`);
- every subquestion has at least one capability;
- the checklist is not decoration: modeling claims IDs, code plans `validate_capability()` assertions, reviewers run a `capability_contract` check, and the paper may claim only capabilities that passed.

## 4. Modeling Hardening

### Assumption precheck

Before finalizing assumptions, on the simplest subquestion:

1. list every ambiguous statement with at least two plausible readings;
2. compute both readings cheaply (hand calculation, spreadsheet, a few lines);
3. check progression: later subquestions must respond visibly to new constraints or resources; if a result barely changes, the assumption is suspect;
4. record the chosen reading, the rejected reading, and the reason.

If the choice changes what the team can claim, ask the human through one choice card.

### Upgrade handling

When the problem implies a mechanism that upgrades a classic formulation (rechargeable vehicles → multi-trip routing; time windows → visit intervals; robustness → multi-scenario):

1. review every upgrade hint from the parse/classification;
2. adopt it by default — implementable mechanisms are not optional;
3. reject only with a reason: physical/business infeasibility, contradicting data, or a solver bound with an explicit expected error margin.

Missing parameters are not a reason to skip. Make an explicit justified assumption, list it, and mark it for sensitivity analysis. If you adopt a simplified upgrade, keep its core mechanism and say what was simplified.

## 5. Code and Results Rules

### Anti-degradation

The implementation must realize the approved method, not a more convenient replacement:

- no proxy labels (file IDs, filenames, row indices);
- no same-data derived features predicting derived labels (circular validation);
- no string/word matching standing in for a semantic capability;
- no scoring without performing the claimed downstream action;
- every `falsifiable_check` becomes a runtime assertion that raises on failure; deleting or weakening it to pass review is a violation.

If a capability truly cannot be implemented, degrade the claim through the human decision path — never through a comment in code.

### Data self-check

Full-precision results are written to disk, but agents read only summaries:

- never `Read`/`cat` an entire results JSON;
- audit scripts recompute at full precision and print only conclusions: `PASS`/`FAIL`, violation count, max error, at most five violation locations;
- figures and tables are generated from saved data, never from hard-coded numbers in a plotting script.

### Constraint closure audit

When hard constraints exist:

1. recompute every constraint from the final result file — never trust the optimizer's own `constraints_ok`;
2. audit every comparison baseline with the same script; auto-discover keys containing `baseline`, `naive`, `greedy`, `就近`, `等权`, `不调整`, or `lower_bound` and fail the audit if any is missing;
3. a constraint-violating baseline is either fixed or explicitly labeled infeasible/theoretical lower bound in the paper;
4. record the credential:

```text
<!-- AUDIT_OK source=results.json rechecked_at=<timestamp> n_constraints=N -->
```

When the problem has no hard constraints, record `n_constraints=0` with a one-line statement.

## 6. Figure Manifest

Every planned figure is registered in a machine-readable block so generation and auditing can reconcile plan with products:

```text
<!-- BEGIN FIGURE_MANIFEST -->
**Data figures**
- fig_q2_residual_diag [4-panel] — residual diagnostics — competition#5 — section: Q2 validation
- fig_q3_pareto — Pareto front — competition#8 — section: Q3 solving
**TikZ figures**
- tikz_feasible_q2 — feasible region with constraints — section: Q2 model
<!-- END FIGURE_MANIFEST -->
```

Manifest rules:

- IDs use `fig_`/`tikz_` prefixes;
- each entry names a concrete chart type, its evidence source (recipe ID or `custom`), and the target section;
- the same chart type appears at most three times;
- TikZ is reserved for coordinate-defined geometry (feasible region, phase plane, force diagram, network topology); function curves and distributions are data figures;
- multi-panel combinations are explicit (`[2-panel]`/`[4-panel]`), with at most 4 panels and readable panel width;
- perception/reconstruction tasks plan a real-sample before/after comparison figure ahead of metric figures;
- reference density: 12–20 data figures is a typical competition range, with 3 as a hard floor; plan by problem complexity, not by quota.

Type 3/4 figures additionally pass `figure-vision-review` before G5:

- verdicts are `PASSED`, `NEEDS_FIX`, or `NOT_RUN`, recorded in
  `paper/audits/vision_figure_review.md`;
- `NEEDS_FIX` blocks the figure until it is rerendered and re-reviewed;
- `NOT_RUN` is allowed only with a human waiver
  (`decision_type: figure_vision_review_waiver`) in
  `planning/framing_decisions.jsonl`;
- the external vision API key never appears in files or reports; it is read
  from the environment variable named in `planning/vision_config.json`
  (`key_env`, default `VISION_API_KEY`).

## 7. Paper Output Norms

### Output format

- Default paper output is LaTeX: `paper/main.tex` + `paper/sections/*.tex` +
  `paper/refs.bib`, compiled to PDF.
- Markdown is an intermediate drafting format only; sections are converted to
  `.tex` before writer handoff.
- Word/`.docx` is not a default deliverable; produce it only when the contest
  profile explicitly requires it.

### Structure

Competition papers keep the standard skeleton (abstract → restatement → assumptions → symbols → per-question modeling and solving → sensitivity/validation → evaluation → references → appendix code). Statistics-modeling papers design content-driven chapters, but chapter titles must be specific and core analysis chapters occupy roughly 40–50% of the paper.

### Abstract

- Write the abstract last, after every section and `RESULTS.md` exist; writing it first means inventing numbers.
- One paragraph per subquestion; no paragraph contains two or more "针对问题/Problem N" anchors.
- Every number in the abstract appears identically in the body.
- Typical lengths: 400–600 characters for most Chinese contests; 500–700 for statistics modeling; rich mode (e.g., Huawei Cup) 1500–2200 with 8–12 keywords.

### Page estimate

- Use one density: 900 Chinese characters per page by default.
- Count only `paper/sections/`; abstract, TOC, references, and appendix code are excluded.
- Code blocks never live in body sections; they go to the appendix, otherwise the page estimate is inflated.
- Any subquestion section below ~4 pages (~3500 characters) must be expanded.

### References

- BibTeX is fetched and verified, never written from memory.
- First-use numbering is strictly increasing; multi-citations merge in ascending order.
- Chinese competition templates use superscript citations with the template-correct command (`\upcite` vs `\cite`).
- Citation keys are descriptive (`author_year_topic`), with a `TODO__` prefix when metadata is still unknown.

### Number traceability

- Every claim-relevant number in the paper exists in `frozen_numbers.json` or the current result JSON.
- Result summaries carry the `AUDIT_OK` credential when constraint auditing applies.
- No historical result files remain.
- Unrealistic "perfect" values are flagged: R²/accuracy > 0.999, zero error, p-value = 0, or improvements above ~10× need explicit justification.

### Placeholders

No `TODO`, `待补充`, `[论文标题]`, or template sentinels remain in sections or the abstract.

## 8. Compliance Pre-flight

`output-standards-auditor` runs these named checks in `submission` mode and saves `paper/audits/output_spec_report.md`:

| Check | Passes when |
|---|---|
| `artifact_contract` | canonical files exist at minimum sizes; naming contract holds; no stale result versions |
| `figure_manifest` | every planned figure exists and is embedded; no embedded figure is missing from disk; every entry has type, source, section |
| `figure_vision_review` | every embedded Type 3/4 figure has a verdict; `NEEDS_FIX` blocks; `NOT_RUN` requires a human waiver; report contains no API key |
| `page_estimate` | one density; body sections only; no code in body; no thin subquestion chapters |
| `abstract_format` | abstract written last; per-question paragraphs; numbers match body |
| `number_traceability` | numbers trace to frozen/current artifacts; audit credentials present; no unrealistic values without justification |
| `reference_contract` | real references; increasing first-use numbers; correct template citation command |
| `placeholder_freedom` | no placeholders in sections or abstract |
| `format_compliance` | anonymity, TOC, required abstracts, `longtable` symbol table, no `babel[english]` in Chinese templates, no body code blocks; contest rules verified against the current official source |

The report is a pre-flight: it feeds the three G6 auditors (consistency, completeness, QA) and never replaces them. A `FAILED` verdict blocks final assembly.

## 9. How the Skills Implement This

| Rule | Skill |
|---|---|
| Capability checklist | `capability-contract-builder` |
| Assumption precheck and upgrade handling | `model-assumptions-builder` |
| Anti-degradation code plan | `model-code-analyzer` |
| `capability_contract` review check | `python-code-reviewer`, `matlab-code-reviewer` |
| Constraint closure audit | `robustness-checker` |
| Figure manifest | `figure-table-planner`, `math-figure-generator` |
| Figure vision review | `figure-vision-review`, `workflow-orchestrator` |
| Output pre-flight audit | `output-standards-auditor` |
| Routing | `workflow-orchestrator` |

## 10. Boundaries

- This specification is mechanical. It never picks a method, interprets a number, or invents a contribution; those stay with the human through the decision ledger.
- Contest AI-use and format rules change every year and differ by contest. Verify the current official rules before submission; this repo encodes no contest's authoritative policy.
- A passing output audit does not make a paper ready. The three G6 auditors remain the final word.
