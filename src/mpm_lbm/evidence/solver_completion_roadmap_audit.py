from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json


def build_solver_completion_roadmap_audit(
    root: Path,
    policy_path: str = "configs/step63_solver_completion_roadmap_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [roadmap_row(item) for item in policy["roadmap"]]
    steps = [int(row["step"]) for row in rows]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "first_step": min(steps) if steps else 0,
        "last_step": max(steps) if steps else 0,
        "step68_step76_roadmap_exists": steps == list(range(68, 77)),
        "premature_activation_count": sum(
            1 for row in rows if row["status"] != "planned" or row["activated_in_batch_a"]
        ),
        "solver_completion_roadmap_pass": False,
    }
    summary["solver_completion_roadmap_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step68_step76_roadmap_exists"]
        and summary["premature_activation_count"] == 0
    )
    return rows, summary


def roadmap_row(item: dict) -> dict:
    return {
        "step": int(item["step"]),
        "title": item["title"],
        "status": item["status"],
        "new_simulation_required": bool(item["new_simulation_required"]),
        "activated_in_batch_a": False,
        "pass": item["status"] == "planned",
    }
