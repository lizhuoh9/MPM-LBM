# Fluent Official Local Execution Guard

This guard prepares the repository-facing contract for a future local manual
Fluent official two-way FSI run. It does not execute Fluent and does not move
official files into the repository.

No Fluent run is executed by this guard.

Official payloads remain local under benchmarks/private/fluent_fsi_2way/.

This guard does not permit validation claims.

Comparison output is gap-only until a later explicit validation step passes.

## Local-Only Inputs

The official Ansys/Fluent payloads remain outside tracked artifacts:

```text
benchmarks/private/fluent_fsi_2way/fsi_2way.zip
benchmarks/private/fluent_fsi_2way/flap.msh
benchmarks/private/fluent_fsi_2way/steady_fluid_flow.jou
```

Any Fluent case/data files, Workbench project files, generated journals, or
official mesh derivatives are also local-only. They must not be committed.

## Repository Artifacts

The committed repository side of this guard is limited to:

```text
configs/fluent_official_2way_fsi_local_execution_schema.json
configs/fluent_official_monitor_export_schema.json
outputs/fluent_official_local_execution_prep/guard_report.json
```

The schema files describe the manifest and monitor export shape a future local
run may produce. The guard report records that no external action was taken.

## Future Manual Run Boundary

A later explicit step may run Fluent locally only if the user provides the
private files and explicitly approves the external action. That later step must
record:

- exact command and environment;
- local manifest that matches the execution schema;
- monitor export that matches the monitor schema;
- proof that official payloads were not committed;
- gap-only comparison wording unless a separate validation gate passes.

This guard alone cannot upgrade the current LBM-only Step139 result, cannot
enable selected96, and cannot claim quasi-2D, FSI, Fluent, Figure 29.3, or
production readiness.
