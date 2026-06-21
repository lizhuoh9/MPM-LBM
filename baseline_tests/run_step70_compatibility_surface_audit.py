import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.compatibility_surface_audit import build_step70_compatibility_surface_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step70_compatibility_surface_audit, "outputs/step70_compatibility_surface_audit", "logs/step70_compatibility_surface_audit.log", "compatibility_surface_audit_pass", "[OK] Step 70 compatibility surface audit finished")


if __name__ == "__main__":
    main()
