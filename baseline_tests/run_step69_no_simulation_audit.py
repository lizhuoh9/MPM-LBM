import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.step69_no_simulation_audit import build_step69_no_simulation_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_no_simulation_audit, "outputs/step69_no_simulation_audit", "logs/step69_no_simulation_audit.log", "no_simulation_audit_pass", "[OK] Step 69 no simulation audit finished")


if __name__ == "__main__":
    main()
