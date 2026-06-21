import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.step_specific_proxy_legacy_shim_audit import build_step68_legacy_shim_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step68_legacy_shim_audit, "outputs/step68_legacy_shim_audit", "logs/step68_legacy_shim_audit.log", "step68_legacy_shim_audit_pass", "[OK] Step 68 legacy shim audit finished")


if __name__ == "__main__":
    main()
