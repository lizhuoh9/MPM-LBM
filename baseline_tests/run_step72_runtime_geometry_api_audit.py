import os

from step72_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.runtime_geometry_api_audit import build_step72_runtime_geometry_api_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step72_runtime_geometry_api_audit, "outputs/step72_runtime_geometry_api_audit", "logs/step72_runtime_geometry_api_audit.log", "runtime_geometry_api_audit_pass", "[OK] Step 72 runtime geometry API audit finished", "runtime_geometry_api")


if __name__ == "__main__":
    main()
