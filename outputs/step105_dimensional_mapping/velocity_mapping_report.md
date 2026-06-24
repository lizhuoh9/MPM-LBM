# Step105 Velocity Mapping Report

| row_name | n_grid | dx_norm | mpm_dt | lbm_dt_phys | duct_length_m | target_u_lbm | proxy_inlet_velocity_mps | official_inlet_velocity_mps | velocity_ratio | dimensional_velocity_mapping_gap_present | mapping_formula | direct_quantitative_equivalence_allowed | validation_claim_allowed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fluent_duct_flap_proxy_48_50step_transient_gap_smoke | 48 | 0.020833333333333332 | 0.0005 | 0.0005 | 0.1 | [0.02, 0.0, 0.0] | 0.08333333333333333 | 10.0 | 0.008333333333333333 | True | target_u_lbm_x * dx_norm / lbm_dt_phys * duct_length_m | False | False |
