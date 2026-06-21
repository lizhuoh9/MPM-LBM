import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.step_specific_proxy_import_execution_audit import build_step68_import_execution_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step68_import_execution_audit, "outputs/step68_import_execution_audit", "logs/step68_import_execution_audit.log", "step68_import_execution_audit_pass", "[OK] Step 68 import execution audit finished")


if __name__ == "__main__":
    main()
