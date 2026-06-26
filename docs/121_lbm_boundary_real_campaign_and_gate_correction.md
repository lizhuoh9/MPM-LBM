# Step121 LBM Boundary Real Campaign And Gate Correction

Step121 is a campaign-controller correction for the LBM boundary repair work
started in Steps 119 and 120.

It does not change the validation scope to quasi-2D or FSI. It keeps the work in
LBM-only duct and static two-flap gates until real 48^3 and selected 96^3
evidence is available.

## Corrected Semantics

Step121 separates campaign state from final classification.

Pending rows are no longer treated as failed physics evidence. A failure
classification is allowed only when both real 48^3 candidate rows have executed
and both fail hard gates.

Campaign states:

- `awaiting_48_references`
- `awaiting_48_candidates`
- `48_candidates_failed`
- `best_48_selected`
- `awaiting_selected_96_duct`
- `awaiting_selected_96_static`
- `complete`

Final classifications:

- `boundary_repair_partial_continue_lbm`
- `boundary_repair_failed_revisit_lbm_solver`
- `boundary_repair_success_go_to_quasi2d`

Success remains blocked unless references complete, one 48^3 candidate is
selected, selected 96^3 duct passes, selected 96^3 static two-flap passes, and
selected-chain limiter/failure gates pass.

## Phase Entry Points

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase references48 --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase candidates48 --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected96 --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected-static --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary
```

The selected 96^3 phases require a best-selection artifact. This prevents a
manual 96^3 row from being presented as selected-chain proof before 48^3
selection exists.

## Artifact Contract

Step121 writes its authoritative artifacts under:

`outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`

Important files:

- `step121_summary.json`
- `step121_best_boundary_selection.json`
- `step121_gate_report.json`
- `solver_report.json`

The output directory may also contain Step120 compatibility files because the
actual row execution still uses the Step120 row runner. Step121 status should be
read from the `step121_*` files.

## Runtime Storage

Raw checkpoints and raw failure arrays are intentionally ignored by Git:

- `outputs/tmp/step121_checkpoints/`
- `outputs/tmp/step121_failure_snapshots/`
- `outputs/tmp/step120_checkpoints/`
- `outputs/tmp/step120_failure_snapshots/`

Committed failure artifacts should contain only stats, local anomaly location,
and a pointer to the ignored runtime payload.

## Current Evidence State

The committed Step121 artifact is a smoke run only:

- phase: `smoke`
- row: `tiny_step121_real_runner_smoke`
- campaign state: `awaiting_48_references`
- final classification: `boundary_repair_partial_continue_lbm`
- quasi-2D allowed: `false`

No 48^3 or 96^3 physical success claim is made by this artifact.
