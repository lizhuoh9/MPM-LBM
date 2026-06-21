import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.batch_migration_audit import build_batch_migration_audit


POLICY_PATH = "configs/step64_motion_wall_velocity_migration_policy.json"


def build_step64_bridge_retirement_audit(root):
    rows, migration_summary = build_batch_migration_audit(root, POLICY_PATH)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["canonical_forbidden_bridge_token_count"] == 0),
        "temporary_bridge_count_for_step64_files": sum(int(row["canonical_forbidden_bridge_token_count"]) for row in rows),
        "canonical_uses_legacy_getattr_count": sum(1 for row in rows if row["canonical_uses_legacy_getattr"]),
        "migration_audit_pass": bool(migration_summary["batch_migration_audit_pass"]),
        "step64_bridge_retirement_pass": False,
    }
    summary["step64_bridge_retirement_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["temporary_bridge_count_for_step64_files"] == 0
        and summary["canonical_uses_legacy_getattr_count"] == 0
        and summary["migration_audit_pass"]
    )
    return rows, summary


def main():
    os.chdir(ROOT)
    run_audit(
        build_step64_bridge_retirement_audit,
        "outputs/step64_bridge_retirement_audit",
        "logs/step64_bridge_retirement_audit.log",
        "step64_bridge_retirement_pass",
        "[OK] Step 64 bridge retirement audit finished",
    )


if __name__ == "__main__":
    main()
