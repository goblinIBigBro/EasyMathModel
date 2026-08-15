---
name: output-standards-auditor
description: Run a pre-flight audit of the final paper and workspace outputs against the packaged output specification (naming, figure manifest, page estimate, abstract, traceability, references, format compliance) and save one compact report before the three G6 auditors.
---

# Purpose

Catch output-level defects mechanically before the three-auditor layer: planned figures that do not exist, numbers in the paper that no result file produces, abstracts written before the body, page estimates that include appendix code, and contest-format violations that compile silently.

# Preconditions

- `rigor_profile` is `submission`.
- Paper sections are drafted and figures/tables exist.
- `frozen_numbers.json` exists when numerical claims are present.

# Workflow

1. Read the problem frame, capability checklist (when present), figure plan, frozen numbers, and paper files.
2. Run each named check below and record concrete evidence, not bullet counts.
3. Save `paper/audits/output_spec_report.md`.
4. Set verdict: `PASSED`, `FAILED`, or `NOT_RUN`.

# Named Checks

## artifact_contract

- Canonical files exist with their minimum sizes: parse, classification, method cards, decision ledgers, run summaries, frozen numbers.
- Naming follows the workspace contract (`fig_`/`tikz_` prefixes, `problem_N_results.json`, `run_summary.json`, no version-stale result files such as `results_v1.json` left beside current ones).

## figure_manifest

- Every planned figure in the figure plan/manifest exists on disk and is embedded in the paper.
- No figure name is embedded that does not exist.
- Every figure entry names a concrete chart type, its evidence source, and its target section.

## page_estimate

- Body-page estimate uses one consistent density (900 Chinese characters per page by default; contest profile may override).
- Only `paper/sections/` counts; abstract, TOC, references, and appendix code are excluded.
- Code blocks are not in body sections; they belong in the appendix.
- No subquestion section is below the profile minimum (default: ~4 pages / 3500 characters).

## abstract_format

- The abstract was written after the body (no placeholder remains).
- Competition papers split abstract into one paragraph per subquestion; no paragraph contains two or more "针对问题/Problem N" anchors.
- Every number in the abstract also appears in the body.

## number_traceability

- Every claim-relevant number in the paper exists in `frozen_numbers.json` or the current result JSON.
- Result summaries carry an audit credential (e.g., `AUDIT_OK` with source and timestamp) when constraint auditing was required.
- No historical result files remain that could cause version drift.
- Unrealistic "perfect" values (R2/accuracy > 0.999, zero error, p-value = 0) are flagged for justification.

## reference_contract

- Citations are real (BibTeX fetched/verified, not fabricated).
- First-use numbering is strictly increasing; multi-citations are merged and ascending.
- Chinese competition templates use superscript citations and the template-correct command (`\upcite` vs `\cite`).

## placeholder_freedom

- No template placeholders, TODO markers, or "待补充" remain in sections or the abstract.

## format_compliance

- Contest-specific format: anonymity, TOC, Chinese and English abstracts where required, symbol table in `longtable`, no `babel[english]` in Chinese templates, no code blocks in body.
- Time-varying contest rules are verified against the current official source; do not assume last year's rules.

# Rules

- Do not repair findings inside the audit; record the owner and the artifact path.
- Do not replace or rank above the three G6 auditors; a passing output-spec report does not substitute for consistency, completeness, or QA.
- Do not invent thresholds; use the profile constants and the current contest rules.
- Do not claim compliance with a rule you did not verify.
- Flag every blocker explicitly; a `FAILED` verdict blocks final assembly.

# Verification

- Every named check has evidence or a justified `NOT_APPLICABLE`.
- Figure plan and paper agree in both directions.
- Numbers trace to frozen or current result artifacts.
- Verdict matches the findings and the QA layer consumes the report.
