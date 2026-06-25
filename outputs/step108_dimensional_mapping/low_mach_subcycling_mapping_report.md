# Step108 Low-Mach Subcycling Mapping

This mapping keeps the LBM inlet at low Mach while matching the public tutorial 10 m/s inlet speed dimensionally.

| low_mach_mapping_enabled | duct_length_m | n_grid | dx_phys_m | target_inlet_velocity_mps | target_u_lbm | lbm_dt_phys_s | official_fsi_dt_s | lbm_substeps_per_fsi_step | mapped_inlet_velocity_mps | mapped_velocity_error_mps | mapping_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | 0.1 | 48 | 0.0020833333333333333 | 10.0 | 0.02 | 4.166666666666667e-06 | 0.0005 | 120 | 10.0 | 0.0 | True |
