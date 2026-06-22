from step75_common import run_named_audit
from src.mpm_lbm.evidence.post_gate_campaign_policy_audit import build_step75_post_gate_campaign_policy_audit


if __name__ == "__main__":
    run_named_audit(
        build_step75_post_gate_campaign_policy_audit,
        "outputs/step75_post_gate_campaign_policy_audit",
        "logs/step75_post_gate_campaign_policy_audit.log",
        "post_gate_campaign_policy_audit_pass",
        "[OK] Step 75 post-gate campaign policy audit finished",
        "post_gate_campaign_policy",
    )
