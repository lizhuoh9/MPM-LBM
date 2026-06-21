import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.simulation_freeze_audit import build_simulation_freeze_audit


def main():
    os.chdir(ROOT)
    run_audit(build_simulation_freeze_audit, "outputs/step63_simulation_freeze_audit", "logs/step63_simulation_freeze_audit.log", "simulation_freeze_audit_pass", "[OK] Step 63 simulation freeze audit finished", None)


if __name__ == "__main__":
    main()
