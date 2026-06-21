import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.step69_legacy_shim_audit import build_step69_legacy_shim_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_legacy_shim_audit, "outputs/step69_legacy_shim_audit", "logs/step69_legacy_shim_audit.log", "step69_legacy_shim_audit_pass", "[OK] Step 69 legacy shim audit finished")


if __name__ == "__main__":
    main()
