import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.step_specific_proxy_migration_audit import build_step68_step_specific_proxy_migration_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step68_step_specific_proxy_migration_audit, "outputs/step68_step_specific_proxy_migration_audit", "logs/step68_step_specific_proxy_migration_audit.log", "step68_proxy_migration_audit_pass", "[OK] Step 68 step-specific proxy migration audit finished")


if __name__ == "__main__":
    main()
