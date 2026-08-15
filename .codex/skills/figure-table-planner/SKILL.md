---
name: figure-table-planner
description: Plan the smallest set of diagnostic, comparison, paper, and appendix figures or tables needed to support verified mathematical-modeling decisions and claims.
---

# Purpose

Make every visual evidence-bearing. Prefer fewer useful visuals over a decorative inventory.

# Inputs

- method card and decision ledger;
- run summaries and final result analysis;
- robustness evidence;
- solution package and frozen numbers in submission mode;
- existing figures/tables.

# Figure Types

- Type 1 diagnostic: internal debugging; never in the paper.
- Type 2 comparison: main vs usable baseline or a genuinely tested alternative; optional in paper.
- Type 3 paper: directly supports a main claim; required only when the claim benefits materially from a visual.
- Type 4 appendix: supplementary evidence referenced from the main text.

# Workflow

1. List verified claims that need visual or exact tabular support.
2. Reuse an existing artifact when it already communicates the claim.
3. For each proposed visual record:
   - ID and Qx;
   - type;
   - source artifact and frozen claim IDs when applicable;
   - one core claim;
   - chart/table form;
   - target section;
   - status and render needs (Type 3/4 require `figure-vision-review`).
4. Ask the human to confirm judgment-bearing Type 3 claims through one compact choice card when they are not already in the decision ledger.
5. Save `methods/Qx/qx_figure_table_plan.md` only when durable planning is needed. In lean exploration, a compact in-conversation plan is sufficient.

# Planning Heuristics

- Use tables for exact values, parameters, and small comparisons.
- Use plots for trends, distributions, sensitivity, or many-item comparisons.
- Use diagrams for mechanisms, dependencies, and workflows.
- A main-vs-baseline figure needs compatible metrics and the same evaluation setup.
- Do not create a multi-method comparison merely to imply breadth.

# Manifest Contract

When the plan is saved, append a machine-readable figure manifest so generation and auditing can reconcile plan with products:

```text
<!-- BEGIN FIGURE_MANIFEST -->
**Data figures**
- fig_q2_residual_diag [4-panel] — residual diagnostics — competition#5 — section: Q2 validation
- fig_q3_pareto — Pareto front — competition#8 — section: Q3 solving
**TikZ figures**
- tikz_feasible_q2 — feasible region with constraints — section: Q2 model
<!-- END FIGURE_MANIFEST -->
```

Rules for every manifest entry:

- IDs use `fig_`/`tikz_` prefixes; a name without a prefix is silently missed by downstream reconciliation.
- Each entry names a concrete chart type, its evidence source (recipe ID or `custom`), and the target section.
- The same chart type appears at most three times; switch the form for the next comparison.
- TikZ is reserved for true geometric structure drawn by coordinates (feasible region, phase plane, force diagram, network topology). Function curves, trends, and distributions are data figures, never TikZ.
- Multi-panel combinations are explicit (`[2-panel]`/`[4-panel]`); panels stay below 4 and each panel keeps enough width to read.
- Perception/reconstruction tasks plan a real-sample before/after comparison figure ahead of metric figures.
- Type 3/4 entries must be reviewed by `figure-vision-review` after rendering;
  record this in the plan so generation and audits can verify it.

# Rules

- Type 1 never enters the paper.
- Type 3 uses final validated sources and a human-confirmed core claim.
- Do not use unresolved exploratory figures as paper evidence.
- Do not fabricate data, captions, or claims.
- Do not fill plans with placeholder sentinels; pause for one human choice instead.
- Every visual must have a source and purpose.
- Every planned figure has an ID, type, evidence source, and section; the manifest is complete or explicitly skipped.

# Verification

- Each planned visual supports a verified claim.
- Types, sources, sections, and statuses are explicit.
- Type 3 claims trace to human decisions and frozen evidence.
- No unnecessary or decorative visual remains.
- Manifest entries and downstream generated figures reconcile one-to-one.
- Every Type 3/4 plan entry marks its vision-review requirement.
