import os

from step72_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.runtime_geometry_readiness_audit import build_step72_runtime_geometry_readiness_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step72_runtime_geometry_readiness_audit, "outputs/step72_runtime_geometry_readiness_audit", "logs/step72_runtime_geometry_readiness_audit.log", "runtime_geometry_readiness_audit_pass", "[OK] Step 72 runtime geometry readiness audit finished", "runtime_geometry_readiness")


if __name__ == "__main__":
    main()
