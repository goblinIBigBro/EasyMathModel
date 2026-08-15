# Core Philosophy

- **The AI owns mechanical correctness; the human owns modeling judgment.**
- Start from goals, objects, constraints, data, outputs, variables, relationships, and checkable conclusions.
- Do not start from model names or favorite techniques.
- Separate assumptions, observations, derivations, and validated conclusions.
- Preserve evidence that changes a decision; do not create files merely to prove that a skill ran.

# Configuration

`planning/session_config.json` has two independent controls:

```json
{
  "interaction_mode": "learning",
  "rigor_profile": "lean"
}
```

- `interaction_mode`: `learning` or `speed`. It changes question density and when AI suggestions are shown.
- `rigor_profile`: `lean` or `submission`. It changes artifact and audit density, never the human-judgment boundary.
- Default to `learning + lean` in a fresh workspace.
- Use `lean` while exploring and iterating. Switch to `submission` only when preparing writer handoff or final assembly.
- For compatibility, read legacy `{ "mode": "learning" | "speed" }` as `interaction_mode`.

`planning/vision_config.json` records vision capability and the external
vision-model API state:

- `current_model_has_vision`: whether the executing agent can actually view
  rendered images in this session (`true`/`false`/`null` while unknown).
- `external_api`: provider, endpoint, model list, `key_env`, and status
  (`unconfigured`/`skipped`/`pending_probe`/`validated`/`failed`). The API key
  is read from the named environment variable (default `VISION_API_KEY`) and
  is never stored in files, reports, or git.
- `policy`: which figure types require vision review (Type 3/4 by default).
- At session start, `workflow-orchestrator` confirms vision capability; when
  the current model has no vision and no API is configured, it asks the user
  once. Skipping records `external_api.status = "skipped"` and never blocks
  the modeling workflow.
- Type 3/4 figures must be `PASSED` by `figure-vision-review`, or `NOT_RUN`
  covered by a human waiver (`decision_type: figure_vision_review_waiver` in
  `planning/framing_decisions.jsonl`), before G5 passes.

# Repository Skill Copies

- `.codex/skills/` and `.claude/skills/` are two complete, independently usable skill trees.
- Every skill and referenced local resource required at runtime must exist in both trees; neither tree may depend on a wrapper, symlink, or path into the other.
- When a shared skill contract changes, update and validate both copies in the same change.
- Runtime-specific wording may differ only when necessary, but each copy must remain standalone and behaviorally consistent with this policy.

# Workflow Discipline

- Parse before classifying; classify before screening methods.
- Ask the modeler about output form, priority, unacceptable failure, and experiment budget before creating a method shortlist.
- Build a role-based shortlist rather than filling a quota:
  - one `main_candidate`;
  - one `usable_baseline`;
  - at most one `conditional_fallback`.
- Allow only a main candidate plus baseline when no genuine fallback exists.
- A trivial reference that cannot complete the real task is `diagnostic_reference`, not a baseline.
- Fully implement the human-approved main method and usable baseline only. Activate a fallback only when its recorded trigger fires.
- Keep changes minimal, traceable, and reviewable.

# Human Decision Convention

Human decisions are captured in one append-only ledger per subquestion:

`methods/Qx/qx_decisions.jsonl`

Use `planning/framing_decisions.jsonl` for global or pre-subquestion framing decisions made before a Qx method directory exists.

Each line is a JSON object with at least:

```json
{
  "decision_id": "q2_method_choice",
  "decision_type": "method_choice",
  "status": "DECIDED",
  "decided_by": "human",
  "captured_in_mode": "learning",
  "choice": "M2",
  "rationale": "M2 is selected because ...",
  "evidence_refs": ["methods/Q2/probes/risk_probe_summary.json"],
  "decided_at": "ISO-8601 timestamp"
}
```

- The AI may present evidence and options but must not originate the human's choice, rationale, confidence, physical interpretation, or submission authorization.
- The AI may append the user's answer verbatim or faithfully structure it; it must not strengthen or invent the rationale.
- Do not create per-skill `*_modeler_decision.md` files for new work.
- Existing decision Markdown files remain readable during migration but are not required for new work.
- A decision passes only when it is human-authored, evidence-linked, non-empty, and contains no placeholder.

# Choice Cards

Use choice cards only at modeling-judgment points, normally twice per subquestion:

1. Before method screening: output form, interpretability/performance priority, unacceptable failure, experiment budget.
2. After the first meaningful experiment: proceed, adjust, or activate the fallback.

An optional third card may be used before final freeze for claim scope and confidence. Do not ask users to decide mechanically checkable matters.

# Workflow Gates

## G1 — PROBLEM_FRAMED

- Parse, classification, data inventory, success criteria, and human framing exist.

## G2 — METHOD_SCREENED

- `methods/Qx/qx_method_card.md` defines the main candidate, usable baseline, and optional conditional fallback.
- `methods/Qx/probes/risk_probe_summary.json` exists.
- The main candidate and usable baseline pass the applicable risk checks.
- Any fallback has an explicit activation trigger.
- No fixed candidate count or source-line limit is used.

## G2.5 — METHOD_CHOSEN_BY_HUMAN

- `qx_decisions.jsonl` contains a `DECIDED` human `method_choice` record citing probe evidence.
- Code generation is allowed only when G2 and G2.5 both pass.

## G3 — CODE_AND_EXPERIMENT_REVIEWED

- The approved main method and usable baseline ran.
- `results/Qx/experiments/roundN/run_summary.json` records configuration, seed, metrics, outputs, and failures.
- A language review artifact contains the required named checks:
  - `syntax`
  - `input_contract`
  - `method_alignment`
  - `reproducibility`
  - `output_contract`
- New review artifacts use `code/Qx/reviews/qx_<lang>_review.json`. Legacy Markdown reviews may be read during migration.

## G4 — RESULTS_JUDGED_AND_FROZEN

- The human decision ledger contains result, stability, and claim-scope verdicts tied to computed evidence.
- Final result analysis and robustness report exist.
- In `submission` profile, the solution package and immutable `frozen_numbers.json` exist and are current.

## G5 — PAPER_SECTION_READY

- The writer uses the solution package as the primary source.
- Numerical claims come from `frozen_numbers.json`.
- Physical/domain interpretation and contribution claims are human-confirmed.
- Every paper figure passes render verification.
- Every Type 3/4 figure has a `figure-vision-review` verdict: `PASSED`, or
  `NOT_RUN` covered by a human waiver (`decision_type:
  figure_vision_review_waiver` in `planning/framing_decisions.jsonl`).

## G6 — FINAL_AUDIT_PASSED

Run only in `submission` profile. All three must pass:

- cross-media consistency;
- semantic completeness;
- final quality assurance.

# Competition Hardening (Optional)

These mechanisms harden contest work without changing the human-judgment boundary or the lean artifact floor.

## Capability Contract

- For parameter-dense problems (roughly 20+ quantified conditions) or problems with multiple verifiable capabilities, `capability-contract-builder` emits `planning/capability_checklist.json`.
- The checklist converts each required capability into an acceptance item with `judge` (`machine`/`semantic`), `criterion`, optional `required_output`/`machine_check`, a `falsifiable_check`, and a `source_sentence` anchored to the problem text.
- The checklist is a cross-stage contract: modeling claims capability IDs, code implements `falsifiable_check` as a runtime assertion where possible, code reviewers verify `capability_contract`, and paper claims only capabilities that passed.
- A missing checklist does not block G1; when present it is part of the acceptance evidence at G3 and G5.

## Output Specification Audit

- In `submission`, `output-standards-auditor` runs after paper drafting and before the three G6 auditors, saving `paper/audits/output_spec_report.md`.
- It checks the artifact/naming contract, figure-manifest reconciliation, body-page estimation (900 characters per page by default; body sections only), abstract format, number traceability, reference contract, placeholder freedom, and format compliance.
- It is a pre-flight audit, not a fourth G6 auditor; `FAILED` blocks final assembly until repaired.

## Modeling and Coding Hardening

- Before finalizing assumptions, run an assumption precheck: enumerate ambiguous readings, compute both readings on the simplest subquestion, and check that later subquestions respond visibly to new constraints (progression check). Record the choice and reason.
- Mechanisms that upgrade a classic formulation are adopted by default. Missing parameters justify an explicit assumption plus sensitivity analysis, not skipping the mechanism. Reject an upgrade only with physical, data, or solver-bound reasons and an explicit error bound.
- When hard constraints exist, recompute them from the final result file (never trust the optimizer's own flag), audit every comparison baseline with the same script, label constraint-violating baselines as theoretical bounds only, and record an `AUDIT_OK` credential with source and timestamp.
- Proxies are forbidden: labels from file IDs/filenames/row indices, same-data derived features predicting derived labels, string matching standing in for semantic capabilities, and scoring without the claimed downstream action. Degrade a claim through the human decision path rather than hiding the gap in code.
- Full-precision results are saved to disk; agents read summaries and audit scripts print conclusions with at most five violation locations, never whole arrays.

# Risk Probe Contract

The risk probe replaces universal ≤30-line PoCs. It is time-bounded, method-specific, and may use reusable scripts.

`methods/Qx/probes/risk_probe_summary.json` must contain:

- `executability`: can the method produce a legal result?
- `data_coverage`: missingness, effective sample size, imbalance, cardinality, and distribution coverage.
- `assumption_checks`: only checks relevant to the method, such as stationarity, multicollinearity, identifiability, clusterability, or constraint feasibility.
- `output_degeneracy`: variance, unique-output count, top-k mass, entropy/Gini, score or rank concentration, and constraint slack where applicable.
- `perturbation_sensitivity`: response to a small justified perturbation.
- `scale_check`: runtime and memory at representative sizes.
- `verdict`: `PASS`, `CONDITIONAL`, or `FAIL`, with evidence and fallback trigger when conditional.

Do not reject a method merely because an irrelevant generic test is unavailable. Do reject or condition it when a load-bearing assumption fails or its output degenerates.

# Lean Artifact Contract

During exploration, keep only:

```text
planning/session_config.json
planning/vision_config.json            # session state; no API key
planning/framing_decisions.jsonl       # only when global framing decisions exist
planning/manifests/Qx.json
methods/Qx/qx_method_card.md
methods/Qx/qx_decisions.jsonl
methods/Qx/probes/risk_probe_summary.json
results/Qx/experiments/roundN/run_summary.json
```

- `planning/manifests/Qx.json` is the machine-readable state source.
- Derive dashboards from manifests; do not rewrite a large dashboard after every state transition.
- `qx_method_card.md` contains roles, assumptions, risks, fallback triggers, and a compact decision history. Do not maintain a separate iteration log for new work.
- Successful runs store summaries and artifact paths. Persist full console logs only for failures or when needed to reproduce an anomaly.
- Ordinary rounds do not require a Markdown experiment report. Generate one only at a human decision point or for the final round.

# Submission Artifact Contract

Before writer handoff, add:

```text
methods/Qx/qx_final_method_explanation.md
code/Qx/reviews/qx_<lang>_review.json
results/Qx/reports/qx_final_result_analysis.md
robustness/Qx/qx_robustness_report.md
results/Qx/reports/qx_solution_package_for_writer.md
results/Qx/reports/frozen_numbers.json
paper/audits/vision_figure_review.md   # when Type 3/4 figures exist
```

The three critical writer rules remain:

1. No final method explanation, no paper section.
2. No final result analysis, no writer handoff.
3. The writer reads the solution package rather than guessing from scattered results.

# Change Impact and Auditing

Classify a change before auditing:

- `NONE`: scratch files, formatting, comments, non-semantic documentation. No consistency audit.
- `LOCAL`: exploratory code or method-card changes before freeze. Run local tests/review only.
- `CANONICAL`: data schema/units, symbols, equations, parameters, official result values, or figure paths. Run a scoped consistency check for affected Qx.
- `FROZEN`: anything that can change a frozen number or paper claim. Log the thaw, update the canonical source, rerun affected experiments, re-freeze, then run scoped consistency.

Do not run a full-workspace audit merely because multiple files changed. Always run the full three-auditor layer once in `submission` profile before final assembly.

# Frozen Numbers

- Numbers flow code → results → freeze → paper.
- Never edit `frozen_numbers.json` by hand.
- To change a frozen value: **解冻 → 修改 canonical source → 重跑 affected work → 重冻结**.
- Record the reason in `results/Qx/reports/freeze_change_log.md`.
- A freeze is stale when a referenced canonical source is newer than `frozen_at`.

# Experiment Output

Every executed round writes:

```text
results/Qx/experiments/roundN/
├── figures/
├── tables/
├── metrics/
└── run_summary.json
```

Create `logs/` only when a failure, warning, or reproducibility need justifies it.

`run_summary.json` records question, round, approved methods, role, status, inputs, outputs, metric summary, seed, environment, warnings, and fallback-trigger state.

# Modeling and Coding Rules

- Match methods to output, data, interpretability, time, and contest constraints.
- Do not choose complexity for appearance.
- Do not invent data, assumptions, evidence, results, or references.
- Keep assumptions explicit and distinguish necessary from simplifying assumptions.
- Maintain `planning/symbol_table.md`; define every symbol and unit before use.
- Use fixed random seeds.
- Save formal outputs to files; console output alone is not a deliverable.
- Keep raw data untouched under `workspace/data_raw/`; write cleaned copies under `workspace/data_clean/`.

# Figures and Paper

- Type 1 diagnostic: internal only.
- Type 2 comparison: may appear in paper.
- Type 3 paper: must support a main claim and pass publication-quality render checks.
- Type 4 appendix: supplementary and referenced from the main text.
- Type 3/4 figures are vision-reviewed by `figure-vision-review`; a
  `NEEDS_FIX` verdict blocks G5 until the figure is rerendered and re-reviewed;
  `NOT_RUN` requires a human waiver before final assembly.
- Paper claims must remain proportional to tested evidence.
- Mention eliminated methods only when the record helps explain a real trade-off; do not manufacture breadth.

# Verification

- In `lean`, verify the current gate and only the affected artifacts.
- In `submission`, verify all required artifacts, frozen-number lineage, figure
  rendering and vision review, references, and the three independent audits.
- A review or audit passes by completing its named semantic checks, not by reaching an arbitrary bullet count.
- Flag uncertainty and blocking issues explicitly.
- Do not approve final assembly while any G6 auditor fails.
