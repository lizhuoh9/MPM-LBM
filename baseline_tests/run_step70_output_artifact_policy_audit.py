import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.output_artifact_policy_audit import build_step70_output_artifact_policy_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step70_output_artifact_policy_audit, "outputs/step70_output_artifact_policy_audit", "logs/step70_output_artifact_policy_audit.log", "output_artifact_policy_audit_pass", "[OK] Step 70 output artifact policy audit finished")


if __name__ == "__main__":
    main()
