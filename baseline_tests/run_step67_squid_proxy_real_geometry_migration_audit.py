import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.batch_migration_audit import build_batch_migration_audit


POLICY_PATH = "configs/step67_squid_proxy_real_geometry_migration_policy.json"


def build(root):
    return build_batch_migration_audit(root, POLICY_PATH)


def main():
    os.chdir(ROOT)
    run_audit(build, "outputs/step67_squid_proxy_real_geometry_migration_audit", "logs/step67_squid_proxy_real_geometry_migration_audit.log", "batch_migration_audit_pass", "[OK] Step 67 squid proxy real geometry migration audit finished", 'step67_squid_proxy_real_geometry_migration_pass')


if __name__ == "__main__":
    main()
