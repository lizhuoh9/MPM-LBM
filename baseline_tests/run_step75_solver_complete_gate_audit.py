from step75_common import run_named_audit
from src.mpm_lbm.evidence.solver_complete_gate_audit import build_step75_solver_complete_gate_audit


if __name__ == "__main__":
    run_named_audit(
        build_step75_solver_complete_gate_audit,
        "outputs/step75_solver_complete_gate_audit",
        "logs/step75_solver_complete_gate_audit.log",
        "solver_complete_gate_audit_pass",
        "[OK] Step 75 solver-complete gate audit finished",
        "solver_complete_gate",
    )
