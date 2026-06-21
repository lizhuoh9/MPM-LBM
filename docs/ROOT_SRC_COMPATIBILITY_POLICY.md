# Root src Compatibility Policy

The canonical implementation boundary starts under `src/mpm_lbm/` for solver
and support code, and under `experiments/steps/` for quarantined historical
step-specific helpers.

Root `src/*.py` files are acceptable only when they fall into one of these
classes:

| Class | Meaning |
| --- | --- |
| `root_compatibility_shim` | A thin import-only file preserving old import paths after a canonical migration. |
| `approved_legacy_support` | A tracked legacy/root utility that remains approved until a later explicit migration step. |

Files outside these classes are reported as `unknown_requires_review`.

## Shim Rules

Compatibility shims must:

```text
contain the phrase "Compatibility shim"
import from the canonical module with import *
avoid def/class bodies
avoid legacy_getattr bridges
avoid Taichi kernels
stay within the small nonblank-line policy limit
```

## Step69 Final State

Step69 establishes the current post-cleanup root state:

```text
current_root_file_count = 119
root_compatibility_shim_count = 102
approved_legacy_support_count = 17
current_step_specific_proxy_remaining_count = 0
current_root_step_specific_implementation_count = 0
current_migration_required_count = 0
current_unknown_requires_review_count = 0
```

The six remaining Step63 support rows are now canonical implementations with
root shims:

```text
src/mpm_lbm/sim/squid_proxy/region_projection.py
src/mpm_lbm/sim/squid_proxy/region_quality.py
src/mpm_lbm/diagnostics/squid_region_driver.py
src/mpm_lbm/sim/wall_velocity/application_envelope.py
src/mpm_lbm/sim/wall_velocity/consistency.py
src/mpm_lbm/sim/wall_velocity/quality.py
```

Future root `src/` changes should update the inventory and policy evidence in
the same step that changes the public compatibility surface.
