# Generic Solver Architecture Contract

This contract fixes the boundary between the reusable solver core, campaign
drivers, benchmark adapters, and validation reports.

## Contract

Solver core remains benchmark-agnostic.

Benchmark adapters may prepare inputs, manifests, and comparisons, but they
must not change solver equations.

Official Fluent assets stay outside the repository.

Validation claims require explicit artifacts and gates.

Step139 does not select a 96^3 boundary.

## Layer Boundaries

The reusable solver core lives under:

```text
src/mpm_lbm/sim/lbm
src/mpm_lbm/sim/mpm
src/mpm_lbm/sim/coupling
src/mpm_lbm/sim/drivers
src/mpm_lbm/sim/geometry
src/mpm_lbm/sim/monitoring
```

These packages may expose generic configuration, diagnostics, geometry
sampling, and monitor utilities. They must not import from `benchmarks/` or
`experiments/`, and they must not depend on private official Fluent payloads.

Campaign orchestration lives under:

```text
experiments/steps
docs/campaigns
outputs
```

Campaign code may select rows, set bounded parameters, run phases, write
artifacts, and summarize gate decisions. Campaign code must not hide
benchmark-specific behavior inside generic solver formulas.

Benchmark references live under:

```text
benchmarks/public
benchmarks/private
```

`benchmarks/public` may contain committed public digitization notes or derived
public reference data. `benchmarks/private` is reserved for local-only official
assets and must not be committed.

## Fluent Boundary

The project may keep gap-comparison and monitor names that refer to Fluent-like
quantities when those names describe comparison scope. Such names are not
license to import official assets, run Fluent implicitly, or claim Fluent
validation.

Official Fluent case, data, mesh, archive, workbench, and journal payloads
remain local-only. They are not solver-core dependencies and are not committed
artifacts.

## Validation Boundary

The only acceptable validation claim path is artifact first:

```text
runner command
simulation-backed artifact
gate report
report wording
current status document
```

A short-window pass does not create a selected boundary unless the specified
long-window gate also passes. Step139 completed the long window and failed the
final hard gate, so no selected boundary, selected96, selected-static, 96^3,
quasi-2D validation, FSI validation, Fluent validation, Figure 29.3 parity, or
production-readiness claim is allowed.

## Static Guard

`tests/test_step139_generic_solver_architecture_contract.py` enforces this
contract without running a simulation. It checks:

- core solver packages do not import benchmark or campaign surfaces;
- core solver packages do not depend on private official asset paths;
- no private or proprietary official Fluent payload is tracked;
- `docs/01_architecture.md` links back to this contract.
