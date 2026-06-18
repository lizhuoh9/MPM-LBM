# Configs

The `configs/` directory stores JSON examples for the unified Step 10 driver.

## Files

### step10_penalty_default.json

Default penalty-mode driver config. It sets:

```text
coupling_mode = penalty
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
mpm_dt = 4.0e-4
beta_lbm
penalty_force_cap_lbm
```

### step10_moving_boundary_default.json

Default moving-boundary driver config. It sets:

```text
coupling_mode = moving_boundary
mb_reaction_scale
mb_force_cap_norm
dynamic_solid_threshold
```

The values are tuned for small validation baselines and should not be treated as calibrated physical parameters.

### step10_mode_matrix.json

Mode matrix config that lists:

```text
none
penalty
moving_boundary
```

This is used to compare the three driver modes under a common baseline window.

## Loading

Configs are loaded with:

```python
FSIDriverConfig.from_json(path)
```

The driver then calls:

```python
config.make_unified_sim_config()
```

to create the shared `UnifiedSimConfig`.

## Common Fields

- `coupling_mode`: selects `none`, `penalty`, or `moving_boundary`
- `n_grid`: cubic LBM/MPM grid resolution
- `n_particles`: MPM particle count
- `n_lbm_steps`: number of LBM driver steps
- `mpm_substeps_per_lbm_step`: MPM substeps per LBM step
- `mpm_dt`: normalized MPM timestep
- `target_u_lbm`: initial target solid velocity in LBM units
- `gravity`: normalized MPM gravity

## Coupling Fields

- `beta_lbm`: penalty-force gain
- `penalty_force_cap_lbm`: cap for penalty `cell_force`
- `mb_reaction_scale`: moving-boundary reaction scale
- `mb_force_cap_norm`: moving-boundary reaction cap in normalized force units

The current config values are conservative small-scale settings. Larger cases require new validation.
