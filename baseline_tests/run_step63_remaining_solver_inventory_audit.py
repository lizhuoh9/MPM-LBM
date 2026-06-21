import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.remaining_solver_inventory_audit import build_remaining_solver_inventory_audit


def main():
    os.chdir(ROOT)
    run_audit(build_remaining_solver_inventory_audit, "outputs/step63_remaining_solver_inventory_audit", "logs/step63_remaining_solver_inventory_audit.log", "remaining_solver_inventory_pass", "[OK] Step 63 remaining solver inventory audit finished", None)


if __name__ == "__main__":
    main()
