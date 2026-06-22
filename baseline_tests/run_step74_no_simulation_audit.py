from step74_common import run_named_audit
from src.mpm_lbm.evidence.step74_no_simulation_audit import build_step74_no_simulation_audit


if __name__ == "__main__":
    run_named_audit(
        build_step74_no_simulation_audit,
        "outputs/step74_no_simulation_audit",
        "logs/step74_no_simulation_audit.log",
        "no_simulation_audit_pass",
        "[OK] Step 74 no simulation audit finished",
        "no_simulation",
    )
