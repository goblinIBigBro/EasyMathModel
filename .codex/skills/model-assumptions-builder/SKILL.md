---
name: model-assumptions-builder
description: Extract and maintain global and method-specific mathematical-model assumptions from the problem frame, active method cards, data profile, and risk probes, while leaving necessity and impact judgments to the human modeler.
---

# Inputs

- problem parse;
- active method cards;
- data profile and risk-probe summaries;
- question dependency map;
- existing assumptions and human decisions.

Read legacy candidate pools only during migration.

# Workflow

1. Extract explicit problem assumptions and method-induced assumptions.
2. Remove filler statements that do not affect model validity or interpretation.
3. For each assumption record:
   - scope and source;
   - modeling need;
   - applicable method/Qx;
   - validation evidence;
   - mitigation or fallback link.
4. Identify conflicts across Qx.
5. Present unresolved necessity/impact trade-offs in one compact choice card where possible.
6. Log human `assumption_necessity` decisions in `qx_decisions.jsonl`.
7. Save `planning/model_assumptions.md`, transcribing settled human labels and impacts with decision IDs.

# Assumption Precheck

Before finalizing assumptions, run a cheap precheck so a wrong key assumption does not poison every downstream result:

1. List ambiguous statements and at least two plausible readings per statement.
2. For the one or two load-bearing ambiguities, compute both readings on the simplest subquestion (hand calculation, spreadsheet, or a few lines of code).
3. Check question progression: later subquestions should respond visibly to new constraints/resources. If a result barely changes, the selected assumption is suspect.
4. Record the chosen reading, the rejected reading, and the reason in `planning/model_assumptions.md`.
5. If the choice changes what the team can claim, ask the human through one compact choice card instead of silently settling it.

# Upgrade Handling

Competition problems often describe a mechanism that upgrades a classic formulation (e.g., rechargeable vehicles force a multi-trip variant of a routing model). Apply the three-step rule:

1. **Review**: find every statement in the parse/classification that implies an upgrade over the textbook model.
2. **Adopt by default**: if the mechanism is implementable, adopt it. Missing parameters are not a reason to skip; make an explicit, justified assumption, list it, and mark it for sensitivity analysis.
3. **Object only with a reason**: physical/business infeasibility, data that contradicts the mechanism, or solver limits with an explicit expected error bound. Complexity alone, "leave it for a later subquestion," or "the parameter is missing" are not valid objections.

If an upgrade is adopted in simplified form, keep its core mechanism (e.g., multi-trip keeps revisiting a base point; time windows keep visit-time intervals) and say what was simplified.

# Assumption Fields

- ID;
- statement;
- scope;
- source and modeling need;
- human-confirmed type: necessary or simplifying;
- validation method/evidence;
- impact if violated;
- mitigation/fallback;
- decision ID.

# Rules

- Do not invent generic assumptions such as “data are accurate” unless they affect a real dependency.
- Do not finalize necessary/simplifying or impact judgments for the human.
- Do not leave many repeated sentinels in the final file; collect missing judgments through a choice card and stop finalization until answered.
- Revisit an assumption only when its method, evidence, or downstream use materially changes.
- Do not skip an upgrade mechanism because the problem lacks a parameter; assume, document, and sensitivity-test it instead.

# Verification

- Every assumption has a modeling need and source.
- Human-owned labels trace to decisions.
- Probe/robustness evidence addresses load-bearing assumptions.
- Cross-Qx conflicts are resolved or explicit.
- Ambiguity precheck results and progression checks are recorded; upgrade mechanisms are adopted or explicitly rejected with a reason.
