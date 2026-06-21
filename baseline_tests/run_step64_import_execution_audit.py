import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.batch_import_execution_audit import build_batch_import_execution_audit


POLICY_PATH = "configs/step64_motion_wall_velocity_migration_policy.json"


def build(root):
    return build_batch_import_execution_audit(root, POLICY_PATH)


def main():
    os.chdir(ROOT)
    run_audit(build, "outputs/step64_import_execution_audit", "logs/step64_import_execution_audit.log", "batch_import_execution_audit_pass", "[OK] Step 64 import execution audit finished", 'step64_import_execution_pass')


if __name__ == "__main__":
    main()
