import os

from step72_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.runtime_geometry_output_policy_audit import build_step72_runtime_geometry_output_policy_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step72_runtime_geometry_output_policy_audit, "outputs/step72_runtime_geometry_output_policy_audit", "logs/step72_runtime_geometry_output_policy_audit.log", "runtime_geometry_output_policy_audit_pass", "[OK] Step 72 runtime geometry output policy audit finished", "runtime_geometry_output_policy")


if __name__ == "__main__":
    main()
