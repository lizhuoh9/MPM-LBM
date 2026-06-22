import os

from step71_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step71_no_simulation_audit import build_step71_no_simulation_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step71_no_simulation_audit, "outputs/step71_no_simulation_audit", "logs/step71_no_simulation_audit.log", "no_simulation_audit_pass", "[OK] Step 71 no simulation audit finished", "no_simulation")


if __name__ == "__main__":
    main()
