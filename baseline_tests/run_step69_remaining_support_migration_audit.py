import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.remaining_support_migration_audit import build_step69_remaining_support_migration_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_remaining_support_migration_audit, "outputs/step69_remaining_support_migration_audit", "logs/step69_remaining_support_migration_audit.log", "remaining_support_migration_audit_pass", "[OK] Step 69 remaining support migration audit finished")


if __name__ == "__main__":
    main()
