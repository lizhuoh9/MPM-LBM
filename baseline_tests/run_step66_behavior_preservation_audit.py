import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.batch_behavior_preservation_audit import build_batch_behavior_preservation_audit


POLICY_PATH = "configs/step66_diagnostic_geometry_displacement_migration_policy.json"


def build(root):
    return build_batch_behavior_preservation_audit(root, POLICY_PATH)


def main():
    os.chdir(ROOT)
    run_audit(build, "outputs/step66_behavior_preservation_audit", "logs/step66_behavior_preservation_audit.log", "batch_behavior_preservation_audit_pass", "[OK] Step 66 behavior preservation audit finished", 'step66_behavior_preservation_pass')


if __name__ == "__main__":
    main()
