from step74_common import run_named_audit
from src.mpm_lbm.evidence.candidate_manifest_policy_audit import build_step74_candidate_manifest_policy_audit


if __name__ == "__main__":
    run_named_audit(
        build_step74_candidate_manifest_policy_audit,
        "outputs/step74_candidate_manifest_policy_audit",
        "logs/step74_candidate_manifest_policy_audit.log",
        "candidate_manifest_policy_audit_pass",
        "[OK] Step 74 candidate manifest policy audit finished",
        "candidate_manifest_policy",
    )
