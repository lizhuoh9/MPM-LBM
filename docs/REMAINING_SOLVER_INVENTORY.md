# Remaining Solver Inventory

Step 63 classifies root `src/*.py` files so Batch A can distinguish completed migrations from remaining support and step-specific proxy work.

Current inventory evidence:

```text
outputs/step63_remaining_solver_inventory_audit/audit.json
```

Current summary:

| Metric | Value |
| --- | ---: |
| root files classified | 119 |
| root compatibility shims from Batch A | 36 |
| step-specific proxy remaining | 34 |
| temporary bridge tokens | 0 |
| migration-required rows reported | 6 |
| unknown requires review | 0 |

The inventory intentionally leaves `runtime_geometry_wall_velocity_*` and `real_geometry_feasibility.py` out of canonical runtime packages. They are reserved for Step68 migration into `experiments/steps/`.
