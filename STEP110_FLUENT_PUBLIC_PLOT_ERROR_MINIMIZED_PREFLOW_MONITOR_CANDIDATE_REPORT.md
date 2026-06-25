# Step110 Fluent Public-Plot Error-Minimized Candidate With Preflow and Monitor Alignment Report

Step110 is complete as proxy evidence. It selects an error-minimized candidate using a proxy preflow restart, public structural-point proxy monitor alignment, and Step107 public-reference error metrics.

This report is not an official Fluent parity statement and does not assert official case, mesh, data, preflow, or monitor reproduction.

## Result

- Proxy preflow: pass
- Candidate matrix: pass
- Best candidate: `cap_2e-2_E_2e4`
- Best normalized RMS error: `0.04180534371270689`
- Best peak relative error: `0.07188800000000004`
- Best peak time error: `0.009`
- Best shape correlation: `0.9995494768417736`
- Monitor alignment: pass
- Curve diagnostics: pass
- Output guard: pass

## Artifacts

- Proxy preflow: `outputs/step110_proxy_preflow/preflow_report.json`
- Restart: `outputs/step110_proxy_preflow/lbm_preflow_restart.npz`
- Candidate matrix: `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json`
- Best candidate curve: `outputs/step110_error_minimized_candidate_matrix/best_candidate_monitor_timeseries.csv`
- Monitor alignment: `outputs/step110_monitor_alignment/monitor_definition_report.json`
- Curve shape diagnostics: `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json`
- Output guard: `outputs/step110_output_guard/output_guard_report.json`
- Artifact manifest: `outputs/step110_artifact_manifest/artifact_manifest.json`

## Step111 Gate

The Step111 gate should use the stricter thresholds from the goal file. If those thresholds are not met in future real-run evidence, Step111 should shift toward structural dynamics or reaction-transfer repair instead of expanding runtime.
