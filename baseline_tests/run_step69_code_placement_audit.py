import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.step69_code_placement_audit import build_step69_code_placement_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_code_placement_audit, "outputs/step69_code_placement_audit", "logs/step69_code_placement_audit.log", "code_placement_audit_pass", "[OK] Step 69 code placement audit finished")


if __name__ == "__main__":
    main()
