import os

from step72_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step72_no_simulation_audit import build_step72_no_simulation_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step72_no_simulation_audit, "outputs/step72_no_simulation_audit", "logs/step72_no_simulation_audit.log", "no_simulation_audit_pass", "[OK] Step 72 no simulation audit finished", "no_simulation")


if __name__ == "__main__":
    main()
