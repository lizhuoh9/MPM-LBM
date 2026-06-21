import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.step_specific_proxy_policy_audit import build_step68_step_specific_proxy_policy_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step68_step_specific_proxy_policy_audit, "outputs/step68_step_specific_proxy_policy_audit", "logs/step68_step_specific_proxy_policy_audit.log", "step68_proxy_policy_audit_pass", "[OK] Step 68 step-specific proxy policy audit finished")


if __name__ == "__main__":
    main()
