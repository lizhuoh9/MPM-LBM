PROXY_RECORD_METADATA = {
    "record_kind": "proxy_diagnostic_record",
    "solver_time_integration_run": False,
    "completed_lbm_steps_source": "config_declared_proxy_steps",
    "total_mpm_substeps_source": "config_declared_proxy_substeps",
    "rho_velocity_source": "proxy_formula",
    "hydro_force_source": "proxy_formula",
    "nan_inf_source": "finite_input_proxy_assumption",
}


def add_proxy_record_metadata(row: dict) -> dict:
    row.update(PROXY_RECORD_METADATA)
    return row


def add_proxy_step_metadata(step: dict) -> dict:
    step.update(PROXY_RECORD_METADATA)
    return step


def proxy_metadata_fields() -> list[str]:
    return list(PROXY_RECORD_METADATA)


def proxy_metadata_present(row: dict) -> bool:
    return all(row.get(key) == value for key, value in PROXY_RECORD_METADATA.items())
