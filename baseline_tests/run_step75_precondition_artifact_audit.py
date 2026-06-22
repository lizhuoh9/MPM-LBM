from step75_common import run_named_audit
from src.mpm_lbm.evidence.precondition_artifact_audit import build_step75_precondition_artifact_audit


if __name__ == "__main__":
    run_named_audit(
        build_step75_precondition_artifact_audit,
        "outputs/step75_precondition_artifact_audit",
        "logs/step75_precondition_artifact_audit.log",
        "precondition_artifact_audit_pass",
        "[OK] Step 75 precondition artifact audit finished",
        "precondition_artifact",
    )
