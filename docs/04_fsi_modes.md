# FSI Modes

`FSIDriver3D` exposes three modes. The modes share initialization, projection, diagnostics, and output handling, but they deliberately keep different coupling paths separate.

| mode | Purpose | Coupler | LBM force | Solid mask | MPM reaction |
| ---- | ------- | ------- | --------- | ---------- | ------------ |
| none | baseline | none | zero | no dynamic solid | none |
| penalty | diffuse-interface MVP | `PenaltyFSICoupler3D` | `cell_force` | no dynamic solid | sampled `hydro_force` |
| moving_boundary | sharper-interface MVP | `MovingBoundaryFSICoupler3D` | zero `cell_force` | dynamic solid | link-wise `hydro_force` |

## none

Purpose: confirm that the LBM and MPM systems can coexist under one driver without coupling forces.

```text
projector.project()
lbm.step()
solid.substep()
```

In this mode, `cell_force` and `hydro_force` remain zero.

## penalty

Purpose: run the diffuse-interface penalty-force MVP from Steps 6 and 7 under the shared driver.

```text
projector.project()
penalty_coupler.build_penalty_force()
lbm.step()
penalty reaction -> MPM grid
```

This mode uses `lbm.step()` and nonzero `cell_force`. The reaction is transferred through `PenaltyFSICoupler3D`.

## moving_boundary

Purpose: run the Step 8 and Step 9 moving-boundary MVP under the shared driver.

```text
projector.project()
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
moving-boundary reaction -> MPM grid
```

This mode uses `step_moving_bounceback()` explicitly. It keeps `cell_force` at zero and transfers the moving-boundary reaction through `MovingBoundaryFSICoupler3D`.

## Boundary Between Modes

The penalty path and moving_boundary path are not merged. This matters because the penalty path is diffuse-interface forcing, while the moving_boundary path is link-wise moving bounce-back plus engineering-scale reaction transfer.
