# Step111 Fluent Public-Plot Real Solver Candidate Materialization Report

Step111 replaces Step110 proxy selection evidence with a real LBM preflow restart and a real FSIDriver3D candidate run for `cap_2e-2_E_2e4`.

The allowed claim is limited to a real solver run over the public tutorial time window compared against the Step107 public-plot digitization.

## Result

- Real LBM preflow: pass
- Real solver candidate: pass
- Real monitor extraction: pass
- Real monitor error comparison: fail
- Output guard: pass

## Artifacts

- Preflow report: `outputs/step111_real_lbm_preflow/preflow_report.json`
- LBM restart: `outputs/step111_real_lbm_preflow/lbm_preflow_restart.npz`
- Solver report: `outputs/step111_real_solver_candidate/real_solver_candidate_report.json`
- Monitor report: `outputs/step111_real_solver_candidate/monitor_definition_report.json`
- Error report: `outputs/step111_error_comparison/error_report.json`
- Guard report: `outputs/step111_output_guard/output_guard_report.json`
- Artifact manifest: `outputs/step111_artifact_manifest/artifact_manifest.json`

## Step112 Gate

If the real candidate does not improve public-plot metrics enough for the next target, Step112 should repair structural dynamics or reaction transfer before expanding the candidate search.
