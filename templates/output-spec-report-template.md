# Output Specification Audit Report

> Saved by `output-standards-auditor` as `paper/audits/output_spec_report.md`. Pre-flight check before the three G6 auditors; it does not replace them.

## Verdict

**VERDICT**: `PASSED` / `FAILED` / `NOT_RUN`

**Audited at**: ISO-8601

**Profile**: `submission`

## Named Checks

### artifact_contract

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] canonical files exist with minimum sizes
- [ ] naming contract holds (`fig_`/`tikz_` prefixes, result JSON names)
- [ ] no stale result versions beside current files

### figure_manifest

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] every planned figure exists on disk
- [ ] every planned figure is embedded in the paper
- [ ] no embedded figure is missing from disk
- [ ] every manifest entry has chart type, evidence source, and section

### page_estimate

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] one density used (900 chars/page default)
- [ ] body sections only counted
- [ ] no code blocks in body sections
- [ ] no subquestion section below the profile minimum

### abstract_format

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] abstract written after the body (no placeholder)
- [ ] one paragraph per subquestion
- [ ] abstract numbers match body numbers

### number_traceability

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] claim-relevant numbers trace to frozen/current artifacts
- [ ] `AUDIT_OK` credential present where constraints were audited
- [ ] no unrealistic perfect values without justification

### reference_contract

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] references are real and verified
- [ ] first-use numbering strictly increasing
- [ ] template-correct citation command used

### placeholder_freedom

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] no TODO / 待补充 / template sentinels in sections or abstract

### format_compliance

Status: `PASS` / `FAIL` / `NOT_APPLICABLE`

Evidence:

- [ ] anonymity, TOC, required abstracts
- [ ] symbol table uses `longtable`
- [ ] no `babel[english]` in Chinese templates
- [ ] contest rules verified against the current official source

## Findings

### Blocking

- [path] description — owner

### Non-blocking

- [path] description — owner

## Handoff

This report feeds `consistency-auditor`, `completeness-auditor`, and `quality-assurance-auditor`. A `FAILED` verdict blocks final assembly.
