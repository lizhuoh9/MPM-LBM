import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.batch_legacy_shim_audit import build_batch_legacy_shim_audit


POLICY_PATH = "configs/step65_runtime_geometry_migration_policy.json"


def build(root):
    return build_batch_legacy_shim_audit(root, POLICY_PATH)


def main():
    os.chdir(ROOT)
    run_audit(build, "outputs/step65_legacy_shim_audit", "logs/step65_legacy_shim_audit.log", "batch_legacy_shim_audit_pass", "[OK] Step 65 legacy shim audit finished", 'step65_legacy_shim_pass')


if __name__ == "__main__":
    main()
