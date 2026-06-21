import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.step69_import_execution_audit import build_step69_import_execution_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_import_execution_audit, "outputs/step69_import_execution_audit", "logs/step69_import_execution_audit.log", "step69_import_execution_audit_pass", "[OK] Step 69 import execution audit finished")


if __name__ == "__main__":
    main()
