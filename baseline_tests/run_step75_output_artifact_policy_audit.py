from step75_common import run_named_audit
from src.mpm_lbm.evidence.step75_output_artifact_policy_audit import build_step75_output_artifact_policy_audit


if __name__ == "__main__":
    run_named_audit(
        build_step75_output_artifact_policy_audit,
        "outputs/step75_output_artifact_policy_audit",
        "logs/step75_output_artifact_policy_audit.log",
        "output_artifact_policy_audit_pass",
        "[OK] Step 75 output artifact policy audit finished",
        "output_artifact_policy",
    )
