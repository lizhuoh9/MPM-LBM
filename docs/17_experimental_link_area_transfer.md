# Experimental Link-Area Reaction Transfer

Step 18 adds an opt-in experimental link-area reaction transfer mode.

The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Scope

The new mode is enabled only through:

```text
coupling_mode = "moving_boundary"
reaction_transfer_mode = "link_area_experimental"
```

Existing moving_boundary configs that omit `reaction_transfer_mode` continue to use:

```text
reaction_transfer_mode = "engineering"
```

## Formula

The experimental scale is computed from Step 17 direction-wise accounting:

```text
area_scale = clip(
    |area_weighted_solid_force_x| / (|bb_net_solid_force_x| + eps),
    area_scale_min,
    area_scale_max
)
```

Then MPM particle reactions are computed from the existing moving-boundary hydro force field:

```text
particle_force =
    sampled_hydro_lbm
    * force_density_scale_lbm_to_norm
    * particle_volume
    * reaction_scale
    * area_scale
```

The force is written to `solid.grid_f_ext`. The experimental transfer does not write to `lbm.cell_force`.

## Baselines

Step 18 adds:

- 32^3 link-area transfer sanity
- 32^3 area policy sweep for `uniform`, `inverse_length`, and `length`
- 48^3 box experimental transfer
- 48^3 procedural squid_proxy experimental transfer
- engineering-vs-link-area comparison
- existing engineering moving_boundary regression

These are engineering comparison baselines, not final validation of a sharp-interface method.

Step 19 extends the evidence with:

- 48^3 box link_area_experimental long-run, 50 LBM steps and 500 MPM substeps
- 48^3 procedural squid_proxy link_area_experimental long-run, 30 LBM steps and 300 MPM substeps
- 64^3 box link_area_experimental feasibility, 5 LBM steps and 25 MPM substeps
- 64^3 engineering-vs-link-area comparison
- 48^3 longer engineering-vs-link-area comparison
- Step 18 regression rows for short experimental transfer and default engineering transfer

## Limitations

- opt-in experimental reaction transfer only
- global proxy scaling, not local surface reconstruction
- no change to moving bounce-back
- no change to the engineering `MovingBoundaryFSICoupler3D`
- no new default FSI mode
- no two-phase flow
- no contact angle physics
- no real squid validation
- no squid swimming validation
- no sparse storage work
