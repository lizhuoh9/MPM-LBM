# Step112 Fluent Public-Plot Real Solver Dynamics Repair Matrix Report

Step112 runs real solver dynamics diagnostics and a bounded real FSIDriver3D candidate matrix. It uses real particle-monitor curves only.

This report is not a Fluent validation statement, does not reproduce official mesh/case/data, and does not assert exact monitor equivalence.

## Result

- Dynamics diagnostics: pass
- Candidate matrix: pass
- Best candidate: `cap_1e-2_E_2e4`
- Hard gate: fail
- Stretch gate: fail
- Best normalized RMS error: `0.4655145431890102`
- Best peak relative error: `0.02677667571140307`
- Best shape correlation: `0.07024139776242506`
- Best peak time error: `0.021`
- Output guard: pass

## Artifacts

- Diagnostics: `outputs/step112_real_dynamics_diagnostics/component_monitor_report.json`
- Candidate matrix: `outputs/step112_real_candidate_matrix/candidate_matrix_report.json`
- Output guard: `outputs/step112_output_guard/output_guard_report.json`
- Artifact manifest: `outputs/step112_artifact_manifest/artifact_manifest.json`

## Step113 Gate

If the hard gate is not enough for refinement, Step113 should continue real-solver dynamics or reaction-transfer repair rather than returning to replay curves.
