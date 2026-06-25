import os
import re
from pathlib import Path

from step110_common import ROOT, read_json
from src.mpm_lbm.evidence.step109_common import summary_rows, write_csv_rows, write_json
from src.mpm_lbm.evidence.step112_common import write_log


FIELDS = ["path", "size_bytes", "extension", "step112_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    write_step112_docs()
    policy = read_json("configs/step112_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step112_rows = [row for row in rows if row["step112_related"]]
    total_size = sum(int(row["size_bytes"]) for row in step112_rows)
    summary = {
        "artifact_budget_pass": False,
        "artifact_manifest_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step112_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step112_file_count": len(step112_rows),
        "step112_official_image_count": sum(1 for row in step112_rows if row["extension"] in {".png", ".jpg", ".jpeg", ".svg"}),
        "step112_proprietary_file_count": sum(1 for row in step112_rows if is_official_file(row, policy)),
        "step112_total_size_bytes": total_size,
        "step112_total_size_mb": total_size / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step112_file_count"] <= int(policy["max_step112_file_count"])
        and summary["step112_total_size_mb"] < float(policy["max_step112_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step112_proprietary_file_count"] == 0
        and summary["step112_official_image_count"] == 0
    )
    summary["artifact_manifest_pass"] = bool(summary["artifact_budget_pass"])
    if not summary["artifact_manifest_pass"]:
        raise RuntimeError(f"Step112 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step112_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step112 artifact manifest finished"
    write_log(ROOT, "logs/step112_artifact_manifest.log", [marker, f"step112_file_count={summary['step112_file_count']}"])
    print(marker)


def write_step112_docs():
    diagnostics = read_json("outputs/step112_real_dynamics_diagnostics/component_monitor_report.json")["summary"]
    matrix = read_json("outputs/step112_real_candidate_matrix/candidate_matrix_report.json")["summary"]
    guard = read_json("outputs/step112_output_guard/output_guard_report.json")["summary"]
    lines = [
        "# Step112 Fluent Public-Plot Real Solver Dynamics Repair Matrix Report",
        "",
        "Step112 runs real solver dynamics diagnostics and a bounded real FSIDriver3D candidate matrix. It uses real particle-monitor curves only.",
        "",
        "This report is not a Fluent validation statement, does not reproduce official mesh/case/data, and does not assert exact monitor equivalence.",
        "",
        "## Result",
        "",
        f"- Dynamics diagnostics: {'pass' if diagnostics['real_dynamics_diagnostics_pass'] else 'fail'}",
        f"- Candidate matrix: {'pass' if matrix['candidate_matrix_pass'] else 'fail'}",
        f"- Best candidate: `{matrix['best_candidate_row_name']}`",
        f"- Hard gate: {'pass' if matrix['hard_gate_pass'] else 'fail'}",
        f"- Stretch gate: {'pass' if matrix['stretch_gate_pass'] else 'fail'}",
        f"- Best normalized RMS error: `{matrix['best_normalized_rms_error']}`",
        f"- Best peak relative error: `{matrix['best_peak_relative_error']}`",
        f"- Best shape correlation: `{matrix['best_shape_correlation']}`",
        f"- Best peak time error: `{matrix['best_peak_time_error_s']}`",
        f"- Output guard: {'pass' if guard['output_guard_pass'] else 'fail'}",
        "",
        "## Artifacts",
        "",
        "- Diagnostics: `outputs/step112_real_dynamics_diagnostics/component_monitor_report.json`",
        "- Candidate matrix: `outputs/step112_real_candidate_matrix/candidate_matrix_report.json`",
        "- Output guard: `outputs/step112_output_guard/output_guard_report.json`",
        "- Artifact manifest: `outputs/step112_artifact_manifest/artifact_manifest.json`",
        "",
        "## Step113 Gate",
        "",
        "If the hard gate is not enough for refinement, Step113 should continue real-solver dynamics or reaction-transfer repair rather than returning to replay curves.",
        "",
    ]
    report = "\n".join(lines)
    (ROOT / "STEP112_FLUENT_PUBLIC_PLOT_REAL_SOLVER_DYNAMICS_REPAIR_MATRIX_REPORT.md").write_text(report, encoding="utf-8")
    (ROOT / "docs" / "112_fluent_public_plot_real_solver_dynamics_repair_matrix.md").write_text(report, encoding="utf-8")


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step112_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {"extension": path.suffix.lower(), "path": rel, "size_bytes": int(path.stat().st_size), "step112_related": is_step112_related(rel)}


def is_step112_related(path: str) -> bool:
    lower = path.lower()
    return "step112" in lower or lower in {"docs/112_fluent_public_plot_real_solver_dynamics_repair_matrix.md"}


def is_official_file(row: dict, policy: dict) -> bool:
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(row["path"].lower()).name in names


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step112_", "logs/step112_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
