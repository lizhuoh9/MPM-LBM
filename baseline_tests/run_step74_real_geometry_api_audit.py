from step74_common import run_named_audit
from src.mpm_lbm.evidence.real_geometry_api_audit import build_step74_real_geometry_api_audit


if __name__ == "__main__":
    run_named_audit(
        build_step74_real_geometry_api_audit,
        "outputs/step74_real_geometry_api_audit",
        "logs/step74_real_geometry_api_audit.log",
        "real_geometry_api_audit_pass",
        "[OK] Step 74 real geometry API audit finished",
        "real_geometry_api",
    )
