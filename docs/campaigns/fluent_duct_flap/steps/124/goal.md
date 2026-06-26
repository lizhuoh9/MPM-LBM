# Step124 LBM Boundary 48^3 Real Campaign Execution Goal

## Source Review

This goal implements the review attached after GitHub `main` was confirmed at
commit `516b1aaa4c71d5468ce5ea444a21ffa07741c8bc` with message
`fix: harden step123 boundary campaign decisions`.

Step123 is accepted as directionally correct. It repaired the previous
high-risk campaign-decision gaps:

- terminal evidence is distinct from validation pass;
- solver-state hash is distinct from run-manifest hash;
- completed artifact reuse checks solver state and selected-source provenance;
- selected 96^3 rows require outlet-flow-development evidence;
- selected provenance fails fast when missing;
- tiny smoke artifacts are explicitly blocked from physical-readiness claims.

The current committed smoke evidence remains bounded:

- `campaign_state=awaiting_48_references`
- `final_classification=boundary_repair_partial_continue_lbm`
- `quasi2d_allowed=false`
- `flow_development_gate_pass=false`
- `flux_imbalance_rel_tail_mean` is about `1.00000147`
- outlet flux is nearly zero
- `step120_validation_claimed=false`

Therefore Step124 must not claim quasi-2D, FSI, Fluent validation, or Figure
29.3 parity. Its purpose is the final small gate/current-entry hardening before
the real 48^3 reference and candidate campaign can run.

## Non-Negotiable Scope

Step124 must be a focused campaign-readiness step. It may repair reference
terminal-failure state handling, flow-development gates, manifest-driven
artifact filtering, and current documentation entry points. It must not add a
new solver feature, fake throughput, add another smoke-only proof layer, or
move historical code into a large refactor.

The large code organization work is explicitly deferred until after the real
campaign. The immediate commit should reduce stale-artifact and bad-selection
risk without changing the physical solver formula.

## P0.1 Reference Terminal-Failure State

Problem: Step123 made candidate rows use terminal evidence, but reference
readiness can still require `_real_completed(row)`. If a real 48^3 reference
physically fails early, Step120 may treat it as a terminal stopped-on-failure
artifact while Step121 keeps the campaign forever in `awaiting_48_references`.

Required behavior:

- Split reference terminal handling by reference role.
- Legacy 48^3 reference:
  - must complete and pass baseline stability gates to allow campaign progress;
  - if it stops early on simulation-backed physical failure, campaign state must
    become `48_legacy_reference_failed`;
  - final classification must remain a failure/blocked state and must not run
    candidate or selected 96 phases as if the baseline were valid.
- Old regularized 48^3 reference:
  - may be accepted as comparison evidence if it completes;
  - may also be accepted as failed-baseline comparison evidence if it stops on a
    simulation-backed physical failure;
  - physical failure must be recorded explicitly instead of being treated as an
    incomplete/missing reference.
- Wall-time expiry, manual interruption, placeholder, or non-simulation rows
  must remain non-terminal and keep the campaign awaiting runnable evidence.

Tests:

- legacy reference physical failure stops the campaign;
- old regularized reference physical failure is valid comparison evidence;
- wall-time/interrupted reference remains awaiting evidence.

## P0.2 Dimensionless Flow-Development Gate

Problem: selected 96^3 flow-development currently checks only reported flux
balance, nonzero outlet flux above `1e-12`, and tail mean imbalance. The
already-reported outlet/inlet and midplane/inlet ratios do not control pass/fail,
and `1e-12` is not a meaningful physical throughput threshold.

Required behavior:

- Add a shared flow-development gate for candidate and selected rows.
- The gate must use dimensionless ratios against inlet tail flux:
  - `abs(inlet_flux_tail_mean) > inlet_flux_min`;
  - outlet and inlet direction must be physically consistent for a through-flow
    duct;
  - `0.80 <= abs(outlet_flux_tail_mean / inlet_flux_tail_mean) <= 1.20`;
  - `0.80 <= abs(midplane_mean_ux_tail_mean / inlet_mean_ux_tail_mean) <= 1.20`
    or the existing midplane/inlet equivalent;
  - `flux_imbalance_rel_tail_mean < 0.10`;
  - `flux_imbalance_rel_tail_max < 0.20` when tail max is available;
  - `outlet_flux_tail_cv < 0.10`.
- Missing required fields must fail the gate with explicit rejection reasons.
- Runtime hard-stop thresholds must stay separate from formal acceptance
  thresholds.

Recommended thresholds:

- hard stop:
  - mass drift above 5%;
  - rho outside `[0.85, 1.15]`;
  - Mach above `0.35`;
  - negative population fraction above `1e-3`.
- formal 48^3 candidate acceptance:
  - absolute final mass drift below `0.5%`;
  - Mach below `0.20`;
  - flux imbalance tail mean below `0.10`;
  - outlet/inlet throughput ratio in `[0.80, 1.20]`;
  - midplane/inlet ratio in `[0.80, 1.20]`;
  - outlet flux tail CV below `0.10`;
  - limiter activation fraction no more than `0.05`.
- selected 96^3 may use 1% mass acceptance, but 5% remains only an early-stop
  safety threshold, not a physical pass threshold.

Tests:

- candidate with zero throughput cannot pass;
- candidate with average-correct but oscillating outlet flux cannot pass;
- selected 96 requires throughput ratio;
- selected 96 missing ratio/CV fields fails formally.

## P0.3 Apply Flow Gate To 48^3 Candidate Selection

Problem: 48^3 candidate selection can still choose a row that is finite and not
obviously unstable but has not developed through-flow to the outlet.

Required behavior:

- 48^3 candidate validation and best-boundary selection must require the shared
  flow-development gate.
- Candidate summaries and selection payloads must expose:
  - `flow_development_gate_pass`;
  - `outlet_to_inlet_flux_ratio_tail_mean`;
  - `midplane_to_inlet_flux_ratio_tail_mean`;
  - `outlet_flux_tail_cv`;
  - `flow_development_rejection_reasons`.
- Best-boundary ordering must treat hard gates first, then throughput/flux
  development, then mass drift, limiter activation, Mach, and runtime.

Tests:

- a candidate with good finite/density/mass fields but bad throughput is
  rejected;
- when two candidates are otherwise passable, the better throughput candidate is
  preferred;
- candidate rejection reasons include the flow-development reason names.

## P0.4 Manifest-Driven Summary Collection

Problem: Step121 summary can scan `output_dir/*/finite_stability_report.json`
and feed all discovered rows into selection/gate logic. Stale same-name rows
with old solver-state hashes, old selected-source provenance, or old campaign
parameters may still participate when the user runs `--phase summary` directly.

Required behavior:

- Add a campaign manifest such as `campaign_manifest.json` for the active
  Step121/Step124 campaign.
- Manifest must include:
  - campaign id;
  - git commit;
  - expected row names;
  - expected solver-state hashes;
  - expected selected-source hashes where relevant;
  - expected schema version;
  - run commands;
  - gate thresholds;
  - artifact root.
- `collect_step121_rows()` must accept only rows matching the active manifest.
- Non-matching artifacts must be reported as ignored, not selected:
  - `stale_artifact`;
  - `provenance_mismatch`;
  - `ignored_by_campaign_gate`.
- Direct `--phase summary` must not allow stale rows to influence reference
  readiness, candidate selection, or selected 96 gates.

Tests:

- summary ignores stale solver-state hash;
- summary ignores wrong selected-source provenance;
- selected static requires the same campaign manifest;
- ignored artifacts are reported with explicit reasons.

## P0.5 Current Documentation Entry Point

Problem: README and root Step files have become a long historical ledger, and
future agents must read too much old context before finding the current campaign
state. Step124 should introduce a stable current-entry surface without moving
historical code or old documents.

Required behavior:

- Add:
  - `docs/current/STATUS.md`;
  - `docs/current/READING_ORDER.md`;
  - `docs/current/ACTIVE_CAMPAIGN.json`;
  - `docs/current/VALIDATION_GATES.md`.
- Add `docs/campaigns/fluent_duct_flap/` as the new location for campaign
  documentation from Step124 forward.
- New Step124 goal/report must live under:
  - `docs/campaigns/fluent_duct_flap/steps/124/goal.md`;
  - `docs/campaigns/fluent_duct_flap/steps/124/report.md`.
- Root README should point to `docs/current/STATUS.md` and the campaign docs,
  but Step124 must not perform a large historical `git mv` cleanup.

Current-entry contract:

- every path in `docs/current/ACTIVE_CAMPAIGN.json.read_first` exists;
- `read_first` has no more than 8 paths;
- active commit matches the current documented campaign commit;
- gate-report state matches `STATUS.md`;
- docs state that quasi-2D, FSI, Fluent validation, and Figure 29.3 parity remain
  blocked.

Tests:

- current docs entry paths exist and are bounded;
- active campaign commit/state matches the committed gate report;
- README links the current entry point.

## P0.6 Validation And Real-Campaign Boundary

Step124 should run focused contract tests and a broader regression pass. Before
launching real 48^3 rows, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q --durations=50
```

Use a 35-40 minute timeout for the full run because Step122/Step123 evidence
showed a 20-minute timeout is too short. If full pytest is still too slow, split
the results honestly into:

- source/config contracts;
- Taichi runtime tests;
- artifact/integration tests.

Do not use `pytest-xdist` for Taichi/GPU tests unless Taichi runtime isolation is
explicitly verified.

Step124 may prepare commands for real 48^3 references and candidates, but it
must not claim that those rows passed unless they actually run to artifact-backed
completion in this step.

## Real Campaign Execution Plan After Step124 Gate Fixes

After Step124 is committed and verified, run 48^3 references without `--force`:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase references48 `
  --allow-large-real-rows `
  --output-interval 25
```

Then refresh summary:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

Then run candidates:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase candidates48 `
  --allow-large-real-rows `
  --output-interval 25
```

If both candidates terminate with real physical failure:

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
```

If at least one candidate passes:

```text
best_boundary_selected = true
campaign_state = best_48_selected
```

Then run selected 96^3 duct-only and selected static only after the prerequisite
gates pass. These selected phases remain LBM-only and do not imply FSI.

## Deliverables

- Step124 goal in the new campaign docs path.
- Step124 report in the new campaign docs path.
- Current-entry docs under `docs/current/`.
- Code changes for reference terminal-failure state handling.
- Code changes for shared dimensionless flow-development gate and CV reporting.
- Code changes for applying that flow gate to 48^3 candidates and selected 96^3
  rows.
- Code changes for manifest-driven summary collection and ignored-artifact
  reporting.
- Focused Step124 tests plus updated Step120/Step121/Step122/Step123 regressions
  where needed.
- Updated README link to the current entry point.
- Exact validation commands and outcomes in the report.
- Commit and push to remote `main` only after verification.

## Success Criteria

Step124 is complete only when:

- legacy reference early physical failure cannot leave the campaign stuck in
  `awaiting_48_references`;
- old regularized reference physical failure can be used as failed-baseline
  comparison evidence;
- zero-throughput and oscillating-flow candidates cannot pass;
- selected 96^3 cannot pass without throughput ratio and tail stationarity;
- summary ignores stale solver-state and wrong selected-source artifacts;
- selected static requires the same campaign manifest;
- current docs tell future runs exactly what to read first;
- full claims remain bounded to LBM campaign readiness, with quasi-2D/FSI/Fluent
  still blocked;
- verification evidence is documented;
- the final commit is pushed to GitHub `main`.
