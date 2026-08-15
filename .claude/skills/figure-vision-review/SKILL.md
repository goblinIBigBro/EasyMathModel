---
name: figure-vision-review
description: Use an external vision model API to review rendered mathematical-modeling figures against a verifiable checklist, manage the vision capability state file, and gate Type 3/4 paper figures before G5/G6.
license: MIT
---

# Purpose

Give the workflow reliable "eyes" when the executing agent cannot view rendered
images. The skill owns the external vision API state, validates the API before
use, reviews figures in two complementary modes (open review + verifiable
checklist), and writes one audit report that G5 and the final auditors consume.

# When to use

- At session start, to bootstrap or report `planning/vision_config.json`.
- After `math-figure-generator` renders any Type 3/4 figure.
- Before `output-standards-auditor` runs its `figure_vision_review` check.
- Whenever the user provides, replaces, or revokes an external vision API.

# Preconditions

- `planning/vision_config.json` exists or the user is willing to answer one
  capability question so it can be created from the template.
- For an API-backed review: the API key is available in the environment
  variable named by `external_api.key_env` (default `VISION_API_KEY`).
- The figures under review exist on disk and were rendered, not merely coded.

# Inputs

- State file: `planning/vision_config.json`.
- Figures: one or more rendered image paths (Type 3/4 required, Type 1/2 optional).
- Optional per-run context: figure ID, figure type, core claim, source artifact,
  target section, and conclusion numbers to verify.

# State File Contract

`planning/vision_config.json`:

```json
{
  "schema_version": 1,
  "current_model_has_vision": null,
  "external_api": {
    "enabled": false,
    "provider": "bigmodel",
    "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "models": ["glm-4.1v-thinking-flash", "glm-4.5v", "glm-4v-plus"],
    "key_env": "VISION_API_KEY",
    "status": "unconfigured",
    "validated_at": null,
    "last_error": null
  },
  "policy": {
    "review_type3_4": true,
    "review_type1_2": false,
    "checklist_required": true,
    "open_review": true,
    "max_image_edge": 1280
  },
  "updated_at": null
}
```

Rules:

- The API key is never stored in this file, in reports, in git, or in logs;
  only `key_env` is recorded.
- `current_model_has_vision` is `true` only when the executing agent can
  actually view rendered images in this session; otherwise `false`. Leave
  `null` only while unknown and resolve it at session start.
- `external_api.status` is `unconfigured`, `skipped`, `pending_probe`,
  `validated`, or `failed`.
- `policy.skip_without_api` is implied by `status: "skipped"`: the workflow
  continues, reviews are recorded as `NOT_RUN`, and final submission needs a
  human waiver in `planning/framing_decisions.jsonl`.

# Workflow

1. **Read state.** Load `planning/vision_config.json`; create it from
   `templates/vision-config.example.json` when absent, then report:
   native vision (`true`/`false`/`null`) and API status.
2. **Resolve capability once per session.** If `current_model_has_vision` is
   `null`, ask the user one compact question: native vision available, provide
   an external vision API, or skip for now. Record the answer in the state
   file. Skipping sets `external_api.status = "skipped"` and never blocks the
   modeling workflow.
3. **Validate a provided API.** When the user supplies an API, update
   `provider`/`endpoint`/`models`/`key_env`, set `status = "pending_probe"`,
   and run `scripts/vision_probe.py`. A successful probe sets
   `status = "validated"`; a failure keeps `failed` with `last_error` and the
   agent reports the error to the user instead of guessing.
4. **Review each figure.** For Type 3/4 (and Type 2 when policy allows):
   run `scripts/figure_vision_review.py --mode both` (checklist is mandatory;
   open review is informational). Use `--context` to pass the claim and
   conclusion numbers the model must verify.
5. **Judge and fix.** A figure with any checklist `FAIL` is `NEEDS_FIX`;
   return it to `math-figure-generator`, rerender, and re-review. A figure is
   `PASSED` only when it has zero `FAIL` items. When the API is skipped or
   unavailable, record `NOT_RUN` and continue.
6. **Write the report.** Save `paper/audits/vision_figure_review.md` with the
   summary table, per-figure verdicts, evidence lines, and raw model output.
   Never include the API key or request payloads.
7. **Hand off.** Report verdicts to the caller; `FAILED` figures block G5,
   `NOT_RUN` requires a human waiver before final assembly.

# Outputs

- Updated `planning/vision_config.json` (state only, no key).
- `paper/audits/vision_figure_review.md`.
- Verdict per figure: `PASSED`, `NEEDS_FIX`, or `NOT_RUN`.

# Output format

The report contains:

- header: generation time, mode, model list, API status;
- summary table: figure, verdict, open-review score (when run), checklist
  PASS/FAIL/UNCERTAIN counts, used model;
- per-figure detail: context, open-review raw output, checklist table with
  evidence, and the exact FAIL items.

# Rules

- Do not put the API key in any file, report, command echo, or log.
- Do not fabricate a review when the API is unavailable; write `NOT_RUN`.
- Do not treat open-review scores as final; checklist `FAIL` is the only
  blocking signal.
- Do not review Type 1 diagnostics unless the user explicitly asks.
- Do not rewrite figures inside this skill; return `NEEDS_FIX` to the figure
  generator with concrete matplotlib-level suggestions.
- Do not modify modeling decisions, frozen numbers, or paper claims.
- Native vision (when available) supplements, not replaces, the checklist when
  the API is configured.

# Verification

- State file exists, has no key, and its `status` is one of the allowed values.
- Every Type 3/4 figure under review has a verdict in the report.
- Checklist items parse to exactly 10 entries per figure (missing entries are
  marked `UNCERTAIN`, never silently dropped).
- `NEEDS_FIX` figures were rerendered and re-reviewed before handoff.
- Report contains no `VISION_API_KEY` value and no request headers.

# Failure modes

- Invalid or expired key (401/403): set `status = "failed"`, report the exact
  HTTP code, ask the user to fix the key, do not retry silently.
- Rate limit (429): retry once after a short pause, then record
  `last_error = "rate_limited"` and mark the run `NOT_RUN` with exit code 3.
- Payload too large (413): recompress to max edge 1024 and retry once.
- Model returns non-conforming output: retry once; if it still fails to parse,
  mark that figure `NOT_RUN` and keep the raw output in the report.
- Network/DNS failure: mark `NOT_RUN`, record the error class, exit 3.

# Stop conditions

- Stop and ask the user when the capability question is unanswered, when a
  provided API cannot be validated, or when a `NEEDS_FIX` figure needs a
  human interpretation of the review.
- Do not keep calling the API after three consecutive failures in one run.

# Handoff

- `PASSED` figures move to `output-standards-auditor` and the G6 layer.
- `NEEDS_FIX` figures return to `math-figure-generator`.
- `NOT_RUN` figures move forward only with a human waiver recorded as
  `decision_type: figure_vision_review_waiver` in
  `planning/framing_decisions.jsonl`.
