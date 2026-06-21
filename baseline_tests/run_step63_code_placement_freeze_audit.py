import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.code_placement_freeze_audit import build_code_placement_freeze_audit


def main():
    os.chdir(ROOT)
    run_audit(build_code_placement_freeze_audit, "outputs/step63_code_placement_freeze_audit", "logs/step63_code_placement_freeze_audit.log", "code_placement_freeze_pass", "[OK] Step 63 code placement freeze audit finished", None)


if __name__ == "__main__":
    main()
