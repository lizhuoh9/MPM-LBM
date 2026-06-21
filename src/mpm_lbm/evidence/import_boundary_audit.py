from __future__ import annotations

import json
from pathlib import Path


def build_import_boundary_audit(root: Path, policy_path: str = "configs/step55_import_boundary_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    sim_root = root / policy["sim_scan_root"]
    rows = []
    for path in sorted(sim_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        lower_text = text.lower()
        forbidden_import_hits = [
            token for token in policy["sim_forbidden_import_tokens"] if token.lower() in lower_text
        ]
        forbidden_path_hits = [
            token for token in policy["sim_forbidden_path_tokens"] if token.lower() in lower_text
        ]
        forbidden_step_hits = [
            token for token in policy["sim_forbidden_step_tokens"] if token.lower() in lower_text
        ]
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "forbidden_import_count": len(forbidden_import_hits),
                "forbidden_path_count": len(forbidden_path_hits),
                "forbidden_step_constant_count": len(forbidden_step_hits),
                "pass": not forbidden_import_hits and not forbidden_path_hits and not forbidden_step_hits,
                "forbidden_import_hits": forbidden_import_hits,
                "forbidden_path_hits": forbidden_path_hits,
                "forbidden_step_hits": forbidden_step_hits,
            }
        )
    summary = {
        "scanned_sim_file_count": len(rows),
        "sim_forbidden_import_count": sum(int(item["forbidden_import_count"]) for item in rows),
        "sim_forbidden_path_count": sum(int(item["forbidden_path_count"]) for item in rows),
        "sim_step_constant_count": sum(int(item["forbidden_step_constant_count"]) for item in rows),
        "solver_behavior_changed": False,
        "import_boundary_audit_pass": False,
    }
    summary["import_boundary_audit_pass"] = bool(
        summary["scanned_sim_file_count"] > 0
        and summary["sim_forbidden_import_count"] == 0
        and summary["sim_forbidden_path_count"] == 0
        and summary["sim_step_constant_count"] == 0
        and not summary["solver_behavior_changed"]
    )
    return rows, summary


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
