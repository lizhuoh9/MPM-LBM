import os
import re
from pathlib import Path

from step110_common import ROOT, read_json, write_log
from src.mpm_lbm.evidence.step109_common import summary_rows, write_csv_rows, write_json


FIELDS = ["path", "size_bytes", "extension", "step110_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    write_step110_docs()
    policy = read_json("configs/step110_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step110_rows = [row for row in rows if row["step110_related"]]
    total_size = sum(int(row["size_bytes"]) for row in step110_rows)
    summary = {
        "artifact_budget_pass": False,
        "artifact_manifest_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step110_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step110_ansys_proprietary_file_count": sum(1 for row in step110_rows if is_official_file(row, policy)),
        "step110_file_count": len(step110_rows),
        "step110_official_image_count": sum(1 for row in step110_rows if row["extension"] in {".png", ".jpg", ".jpeg", ".svg"}),
        "step110_total_size_bytes": total_size,
        "step110_total_size_mb": total_size / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step110_file_count"] <= int(policy["max_step110_file_count"])
        and summary["step110_total_size_mb"] < float(policy["max_step110_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step110_ansys_proprietary_file_count"] == 0
        and summary["step110_official_image_count"] == 0
    )
    summary["artifact_manifest_pass"] = bool(summary["artifact_budget_pass"])
    if not summary["artifact_manifest_pass"]:
        raise RuntimeError(f"Step110 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step110_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step110 artifact manifest finished"
    write_log("logs/step110_artifact_manifest.log", [marker, f"step110_file_count={summary['step110_file_count']}"])
    print(marker)


def write_step110_docs():
    preflow = read_json("outputs/step110_proxy_preflow/preflow_report.json")["summary"]
    candidate = read_json("outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json")["summary"]
    monitor = read_json("outputs/step110_monitor_alignment/monitor_definition_report.json")["summary"]
    curve = read_json("outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json")["summary"]
    guard = read_json("outputs/step110_output_guard/output_guard_report.json")["summary"]
    lines = [
        "# Step110 Fluent Public-Plot Error-Minimized Candidate With Preflow and Monitor Alignment Report",
        "",
        "Step110 is complete as proxy evidence. It selects an error-minimized candidate using a proxy preflow restart, public structural-point proxy monitor alignment, and Step107 public-reference error metrics.",
        "",
        "This report is not an official Fluent parity statement and does not assert official case, mesh, data, preflow, or monitor reproduction.",
        "",
        "## Result",
        "",
        f"- Proxy preflow: {'pass' if preflow['preflow_pass'] else 'fail'}",
        f"- Candidate matrix: {'pass' if candidate['candidate_matrix_pass'] else 'fail'}",
        f"- Best candidate: `{candidate['best_candidate_row_name']}`",
        f"- Best normalized RMS error: `{candidate['best_candidate_normalized_rms_error']}`",
        f"- Best peak relative error: `{candidate['best_candidate_peak_relative_error']}`",
        f"- Best peak time error: `{candidate['best_candidate_peak_time_error_s']}`",
        f"- Best shape correlation: `{candidate['best_candidate_shape_correlation']}`",
        f"- Monitor alignment: {'pass' if monitor['monitor_alignment_pass'] else 'fail'}",
        f"- Curve diagnostics: {'pass' if curve['curve_shape_diagnostics_pass'] else 'fail'}",
        f"- Output guard: {'pass' if guard['output_guard_pass'] else 'fail'}",
        "",
        "## Artifacts",
        "",
        "- Proxy preflow: `outputs/step110_proxy_preflow/preflow_report.json`",
        "- Restart: `outputs/step110_proxy_preflow/lbm_preflow_restart.npz`",
        "- Candidate matrix: `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json`",
        "- Best candidate curve: `outputs/step110_error_minimized_candidate_matrix/best_candidate_monitor_timeseries.csv`",
        "- Monitor alignment: `outputs/step110_monitor_alignment/monitor_definition_report.json`",
        "- Curve shape diagnostics: `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json`",
        "- Output guard: `outputs/step110_output_guard/output_guard_report.json`",
        "- Artifact manifest: `outputs/step110_artifact_manifest/artifact_manifest.json`",
        "",
        "## Step111 Gate",
        "",
        "The Step111 gate should use the stricter thresholds from the goal file. If those thresholds are not met in future real-run evidence, Step111 should shift toward structural dynamics or reaction-transfer repair instead of expanding runtime.",
        "",
    ]
    report = "\n".join(lines)
    (ROOT / "STEP110_FLUENT_PUBLIC_PLOT_ERROR_MINIMIZED_PREFLOW_MONITOR_CANDIDATE_REPORT.md").write_text(report, encoding="utf-8")
    (ROOT / "docs" / "110_fluent_public_plot_error_minimized_preflow_monitor_candidate.md").write_text(report, encoding="utf-8")


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step110_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {"extension": path.suffix.lower(), "path": rel, "size_bytes": int(path.stat().st_size), "step110_related": is_step110_related(rel)}


def is_step110_related(path: str) -> bool:
    lower = path.lower()
    return "step110" in lower or lower in {"docs/110_fluent_public_plot_error_minimized_preflow_monitor_candidate.md"}


def is_official_file(row: dict, policy: dict) -> bool:
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(row["path"].lower()).name in names


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step110_", "logs/step110_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()

