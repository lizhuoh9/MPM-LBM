from __future__ import annotations

import json
from pathlib import Path


def build_step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_audit(
    root: Path,
    matrix_artifact_path: str = (
        "outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix/"
        "squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix.json"
    ),
) -> tuple[list[dict], dict]:
    root = Path(root)
    payload = read_json(root / matrix_artifact_path)
    rows = []
    for row in payload["rows"]:
        rows.extend(
            [
                literal_row(row["row_name"], "driver_run_called", row["driver_run_called"], True),
                literal_row(
                    row["row_name"],
                    "canonical_driver_module",
                    row["canonical_driver_module"],
                    "src.mpm_lbm.sim.drivers.fsi_driver",
                ),
                literal_row(row["row_name"], "completed_lbm_steps", row["completed_lbm_steps"], 3),
                literal_row(row["row_name"], "geometry_type", row["geometry_type"], "squid_proxy"),
                literal_row(row["row_name"], "squid_proxy_enabled", row["squid_proxy_enabled"], True),
                literal_row(row["row_name"], "procedural_geometry_enabled", row["procedural_geometry_enabled"], True),
                literal_row(row["row_name"], "runtime_geometry_enabled", row["runtime_geometry_enabled"], True),
                literal_row(row["row_name"], "wall_velocity_enabled", row["wall_velocity_enabled"], True),
                literal_row(
                    row["row_name"],
                    "combined_runtime_geometry_wall_velocity_enabled",
                    row["combined_runtime_geometry_wall_velocity_enabled"],
                    True,
                ),
                literal_row(row["row_name"], "real_geometry_candidate_enabled", row["real_geometry_candidate_enabled"], False),
                literal_row(row["row_name"], "real_geometry_enabled", row["real_geometry_enabled"], False),
                literal_row(row["row_name"], "link_area_enabled", row["link_area_enabled"], False),
                literal_row(row["row_name"], "write_vtk", row["write_vtk"], False),
                literal_row(row["row_name"], "write_particles", row["write_particles"], False),
                literal_row(row["row_name"], "stable", row["stable"], True),
            ]
        )
    summary = {
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_audit_pass": False,
    }
    summary["step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and payload["summary"]["step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass"] is True
    )
    return rows, summary


def literal_row(row_name: str, check: str, actual, expected) -> dict:
    return {
        "actual": actual,
        "check": check,
        "expected": expected,
        "pass": actual == expected,
        "row_name": row_name,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
