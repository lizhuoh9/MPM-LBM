import os

from step71_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.tau_convention_decision_audit import build_step71_tau_convention_decision_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step71_tau_convention_decision_audit, "outputs/step71_tau_convention_decision_audit", "logs/step71_tau_convention_decision_audit.log", "tau_convention_decision_audit_pass", "[OK] Step 71 tau convention decision audit finished", "tau_convention_decision")


if __name__ == "__main__":
    main()
