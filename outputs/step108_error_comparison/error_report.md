# Step108 Low-Mach Subcycling Error Comparison

This is not Fluent validation. It compares the Step108 low-Mach proxy solver curve against the Step107 approximate public-plot digitization.

| reference_loaded | solver_curve_loaded | monitor_used | monitor_equivalence | sample_count | solver_curve_time_start_s | solver_curve_time_end_s | peak_reference_m | peak_solver_m | peak_abs_error_m | peak_relative_error | rms_abs_error_m | normalized_rms_error | final_reference_m | final_solver_m | final_abs_error_m | final_relative_error | time_of_peak_reference_s | time_of_peak_solver_s | peak_time_error_s | shape_correlation | sign_consistency | all_metrics_finite | validation_claim_allowed | direct_quantitative_equivalence_allowed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | True | free_tip_proxy_mean | False | 51 | 0.0 | 0.025 | 0.000395 | 1.2332112646618043e-06 | 0.0003937667887353382 | 0.9968779461654131 | 0.00024337007157295519 | 0.616126763475836 | 6e-05 | 1.2332112646618043e-06 | 5.87667887353382e-05 | 0.9794464789223033 | 0.004 | 0.025 | 0.021 | 0.07866350821657236 | True | True | False | False |
