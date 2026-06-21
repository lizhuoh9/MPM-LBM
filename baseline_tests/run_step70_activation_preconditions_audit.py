import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.activation_preconditions_audit import build_step70_activation_preconditions_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step70_activation_preconditions_audit, "outputs/step70_activation_preconditions_audit", "logs/step70_activation_preconditions_audit.log", "activation_preconditions_audit_pass", "[OK] Step 70 activation preconditions audit finished")


if __name__ == "__main__":
    main()
