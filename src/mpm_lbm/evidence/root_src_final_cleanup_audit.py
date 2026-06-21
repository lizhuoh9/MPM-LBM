from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import build_step69_current_root_inventory_audit
from src.mpm_lbm.evidence.remaining_support_migration_audit import build_step69_remaining_support_migration_audit


def build_step69_root_src_final_cleanup_audit(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    inventory_rows, inventory = build_step69_current_root_inventory_audit(root)
    migration_rows, migration = build_step69_remaining_support_migration_audit(root)
    rows = [
        check_row("current_root_inventory_audit_pass", inventory["current_root_inventory_audit_pass"], inventory),
        check_row("current_step_specific_proxy_remaining_count", inventory["current_step_specific_proxy_remaining_count"] == 0, inventory["current_step_specific_proxy_remaining_count"]),
        check_row("current_root_step_specific_implementation_count", inventory["current_root_step_specific_implementation_count"] == 0, inventory["current_root_step_specific_implementation_count"]),
        check_row("current_migration_required_count", inventory["current_migration_required_count"] == 0, inventory["current_migration_required_count"]),
        check_row("current_unknown_requires_review_count", inventory["current_unknown_requires_review_count"] == 0, inventory["current_unknown_requires_review_count"]),
        check_row("remaining_support_migration_audit_pass", migration["remaining_support_migration_audit_pass"], migration),
        check_row("migrated_support_count", migration["migrated_support_count"] == 6, migration["migrated_support_count"]),
        check_row("legacy_shim_count_for_six_support_rows", migration["legacy_shim_count_for_six_support_rows"] == 6, migration["legacy_shim_count_for_six_support_rows"]),
        check_row("canonical_imports_legacy_root_count", migration["canonical_imports_legacy_root_count"] == 0, migration["canonical_imports_legacy_root_count"]),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "current_root_file_count": inventory["current_root_file_count"],
        "current_step_specific_proxy_remaining_count": inventory["current_step_specific_proxy_remaining_count"],
        "current_root_step_specific_implementation_count": inventory["current_root_step_specific_implementation_count"],
        "current_migration_required_count": inventory["current_migration_required_count"],
        "current_unknown_requires_review_count": inventory["current_unknown_requires_review_count"],
        "migration_required_count_from_step63": migration["migration_required_count_from_step63"],
        "migrated_support_count": migration["migrated_support_count"],
        "remaining_migration_required_count": migration["remaining_migration_required_count"],
        "legacy_shim_count_for_six_support_rows": migration["legacy_shim_count_for_six_support_rows"],
        "legacy_implementation_body_count_for_six_support_rows": migration["legacy_implementation_body_count_for_six_support_rows"],
        "canonical_imports_legacy_root_count": migration["canonical_imports_legacy_root_count"],
        "inventory_row_count": len(inventory_rows),
        "migration_row_count": len(migration_rows),
        "step69_root_src_final_cleanup_audit_pass": False,
    }
    summary["step69_root_src_final_cleanup_audit_pass"] = bool(
        rows
        and all(row["pass"] for row in rows)
        and summary["current_step_specific_proxy_remaining_count"] == 0
        and summary["current_root_step_specific_implementation_count"] == 0
        and summary["current_migration_required_count"] == 0
        and summary["current_unknown_requires_review_count"] == 0
        and summary["remaining_migration_required_count"] == 0
    )
    return rows, summary


def check_row(name: str, passed: bool, value) -> dict:
    return {
        "check": name,
        "pass": bool(passed),
        "value": value,
    }
