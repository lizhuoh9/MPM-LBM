STATE_GUARD_METHOD_METADATA = {
    "default_driver_state_mutation_count_method": "not_applicable_proxy_no_driver_instance",
    "default_lbm_state_mutation_count_method": "not_applicable_proxy_no_lbm_instance",
    "default_mpm_state_mutation_count_method": "not_applicable_proxy_no_mpm_instance",
    "default_projection_state_mutation_count_method": "not_applicable_proxy_no_projection_instance",
    "persistent_projected_state_count_method": "config_and_artifact_guard",
    "persistent_displaced_geometry_count_method": "config_and_artifact_guard",
    "persistent_lbm_solid_vel_count_method": "config_and_artifact_guard",
    "state_guard_kind": "hash_plus_artifact_scan_plus_not_applicable_proxy_fields",
    "fixed_zero_fields_disclosed": True,
    "hash_checks_method": "measured_config_hash_before_after",
    "forbidden_output_scan_method": "measured_artifact_scan",
}

FIXED_ZERO_STATE_FIELDS = [
    "default_driver_state_mutation_count",
    "default_lbm_state_mutation_count",
    "default_mpm_state_mutation_count",
    "default_projection_state_mutation_count",
    "persistent_projected_state_count",
    "persistent_displaced_geometry_count",
    "persistent_lbm_solid_vel_count",
]


def add_state_guard_truthfulness_metadata(summary: dict) -> dict:
    summary.update(STATE_GUARD_METHOD_METADATA)
    return summary


def state_guard_truthfulness_rows(step_name: str, summary: dict) -> list[dict]:
    rows = []
    for field in FIXED_ZERO_STATE_FIELDS:
        rows.append(
            {
                "check": f"{field}_method_disclosed",
                "pass": f"{field}_method" in summary,
                "value": summary.get(f"{field}_method", ""),
                "notes": f"{step_name} fixed-zero field method must be disclosed",
            }
        )
    rows.extend(
        [
            {
                "check": "fixed_zero_fields_disclosed",
                "pass": summary.get("fixed_zero_fields_disclosed") is True,
                "value": summary.get("fixed_zero_fields_disclosed"),
                "notes": f"{step_name} fixed-zero state fields must be explicitly disclosed",
            },
            {
                "check": "hash_checks_remain_measured",
                "pass": summary.get("hash_checks_method") == "measured_config_hash_before_after",
                "value": summary.get("hash_checks_method"),
                "notes": f"{step_name} hash checks must remain measured",
            },
            {
                "check": "forbidden_output_scans_remain_measured",
                "pass": summary.get("forbidden_output_scan_method") == "measured_artifact_scan",
                "value": summary.get("forbidden_output_scan_method"),
                "notes": f"{step_name} forbidden output scans must remain measured",
            },
        ]
    )
    return rows
