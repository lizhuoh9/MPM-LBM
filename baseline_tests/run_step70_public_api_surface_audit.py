import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.public_api_surface_audit import build_step70_public_api_surface_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step70_public_api_surface_audit, "outputs/step70_public_api_surface_audit", "logs/step70_public_api_surface_audit.log", "public_api_surface_audit_pass", "[OK] Step 70 public API surface audit finished")


if __name__ == "__main__":
    main()
