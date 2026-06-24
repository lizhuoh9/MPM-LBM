from __future__ import annotations

import json
from pathlib import Path


def build_step99_step98_regression_guard(
    root: Path,
    policy_path: str = "configs/step99_step98_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    matrix = read_json(
        root
        / "outputs/step98_48cube_taichi_ggui_visualization_smoke_matrix/48cube_taichi_ggui_visualization_smoke_matrix.json"
    )
    matrix_summary = matrix["summary"]
    quality_summary = read_json(
        root / "outputs/step98_48cube_taichi_ggui_visualization_quality/48cube_taichi_ggui_visualization_quality.json"
    )["summary"]
    activation_summary = read_json(root / "outputs/step98_activation_guard/activation_guard.json")["summary"]
    output_summary = read_json(root / "outputs/step98_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step98_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step98_48cube_taichi_ggui_visualization_quality_pass": quality_summary[
            "step98_48cube_taichi_ggui_visualization_quality_pass"
        ],
        "step98_48cube_taichi_ggui_visualization_smoke_matrix_pass": matrix_summary[
            "step98_48cube_taichi_ggui_visualization_smoke_matrix_pass"
        ],
        "step98_activation_feature_count": activation_summary["activation_feature_count"],
        "step98_activation_guard_pass": activation_summary["step98_activation_guard_pass"],
        "step98_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step98_completed_lbm_steps": matrix_summary["min_completed_lbm_steps"],
        "step98_ggui_screenshot_count": output_summary["step98_ggui_screenshot_count"],
        "step98_ggui_video_count": output_summary["step98_ggui_video_count"],
        "step98_grid_48_enabled_count": matrix_summary["grid_48_enabled_count"],
        "step98_grid_64_enabled_count": matrix_summary["grid_64_enabled_count"],
        "step98_n_grid": matrix_summary["step98_n_grid"],
        "step98_output_guard_pass": output_summary["output_guard_pass"],
        "step98_particle_npy_count": output_summary["step98_particle_npy_count"],
        "step98_runtime_geometry_enabled_count": activation_summary["runtime_geometry_enabled_count"],
        "step98_squid_proxy_enabled_count": activation_summary["squid_proxy_enabled_count"],
        "step98_step94_regression_guard_pass": artifact_value(
            root,
            "outputs/step98_step94_regression_guard/step94_regression_guard.json",
            "step98_step94_regression_guard_pass",
        ),
        "step98_step96_regression_guard_pass": artifact_value(
            root,
            "outputs/step98_step96_regression_guard/step96_regression_guard.json",
            "step98_step96_regression_guard_pass",
        ),
        "step98_step97_regression_guard_pass": artifact_value(
            root,
            "outputs/step98_step97_regression_guard/step97_regression_guard.json",
            "step98_step97_regression_guard_pass",
        ),
        "step98_vtr_count": output_summary["step98_vtr_count"],
        "step98_wall_velocity_enabled_count": activation_summary["wall_velocity_enabled_count"],
        "step99_step98_regression_guard_pass": False,
    }
    summary["step99_step98_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step98_48cube_taichi_ggui_visualization_smoke_matrix_pass"] is True
        and summary["step98_48cube_taichi_ggui_visualization_quality_pass"] is True
        and summary["step98_activation_guard_pass"] is True
        and summary["step98_output_guard_pass"] is True
        and summary["step98_step97_regression_guard_pass"] is True
        and summary["step98_step96_regression_guard_pass"] is True
        and summary["step98_step94_regression_guard_pass"] is True
        and summary["step98_artifact_budget_pass"] is True
        and summary["step98_activation_feature_count"] == int(policy["expected_step98_activation_feature_count"])
        and summary["step98_completed_lbm_steps"] == int(policy["expected_step98_completed_lbm_steps"])
        and summary["step98_n_grid"] == int(policy["expected_step98_n_grid"])
        and summary["step98_grid_48_enabled_count"] == int(policy["expected_step98_grid_48_enabled_count"])
        and summary["step98_grid_64_enabled_count"] == int(policy["expected_step98_grid_64_enabled_count"])
        and summary["step98_squid_proxy_enabled_count"] == int(policy["expected_step98_squid_proxy_enabled_count"])
        and summary["step98_runtime_geometry_enabled_count"]
        == int(policy["expected_step98_runtime_geometry_enabled_count"])
        and summary["step98_wall_velocity_enabled_count"] == int(policy["expected_step98_wall_velocity_enabled_count"])
        and summary["step98_ggui_screenshot_count"] == int(policy["expected_step98_ggui_screenshot_count"])
        and summary["step98_ggui_video_count"] == int(policy["expected_step98_ggui_video_count"])
        and summary["step98_vtr_count"] == int(policy["expected_step98_vtr_count"])
        and summary["step98_particle_npy_count"] == int(policy["expected_step98_particle_npy_count"])
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    actual = artifact_value(root, check["artifact_path"], check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "expected": check["expected"],
        "pass": actual == check["expected"],
        "summary_key": check["summary_key"],
    }


def artifact_value(root: Path, artifact_path: str, summary_key: str):
    payload = read_json(Path(root) / artifact_path)
    return payload.get("summary", payload).get(summary_key)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
