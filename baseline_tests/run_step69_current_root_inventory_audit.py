import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.current_root_inventory_audit import build_step69_current_root_inventory_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_current_root_inventory_audit, "outputs/step69_current_root_inventory_audit", "logs/step69_current_root_inventory_audit.log", "current_root_inventory_audit_pass", "[OK] Step 69 current root inventory audit finished")


if __name__ == "__main__":
    main()
