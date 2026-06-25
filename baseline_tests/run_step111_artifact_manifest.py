import os
import re
from pathlib import Path

from step110_common import ROOT, read_json
from src.mpm_lbm.evidence.step109_common import summary_rows, write_csv_rows, write_json
from src.mpm_lbm.evidence.step111_common import write_log


FIELDS = ["path", "size_bytes", "extension", "step111_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    write_step111_docs()
    policy = read_json("configs/step111_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step111_rows = [row for row in rows if row["step111_related"]]
    total_size = sum(int(row["size_bytes"]) for row in step111_rows)
    summary = {
        "artifact_budget_pass": False,
        "artifact_manifest_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(1 for row in step111_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step111_file_count": len(step111_rows),
        "step111_official_image_count": sum(1 for row in step111_rows if row["extension"] in {".png", ".jpg", ".jpeg", ".svg"}),
        "step111_proprietary_file_count": sum(1 for row in step111_rows if is_official_file(row, policy)),
        "step111_total_size_bytes": total_size,
        "step111_total_size_mb": total_size / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step111_file_count"] <= int(policy["max_step111_file_count"])
        and summary["step111_total_size_mb"] < float(policy["max_step111_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step111_proprietary_file_count"] == 0
        and summary["step111_official_image_count"] == 0
    )
    summary["artifact_manifest_pass"] = bool(summary["artifact_budget_pass"])
    if not summary["artifact_manifest_pass"]:
        raise RuntimeError(f"Step111 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step111_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step111 artifact manifest finished"
    write_log(ROOT, "logs/step111_artifact_manifest.log", [marker, f"step111_file_count={summary['step111_file_count']}"])
    print(marker)


def write_step111_docs():
    preflow = read_json("outputs/step111_real_lbm_preflow/preflow_report.json")["summary"]
    solver = read_json("outputs/step111_real_solver_candidate/real_solver_candidate_report.json")["summary"]
    monitor = read_json("outputs/step111_real_solver_candidate/monitor_definition_report.json")["summary"]
    error = read_json("outputs/step111_error_comparison/error_report.json")["summary"]
    guard = read_json("outputs/step111_output_guard/output_guard_report.json")["summary"]
    lines = [
        "# Step111 Fluent Public-Plot Real Solver Candidate Materialization Report",
        "",
        "Step111 replaces Step110 proxy selection evidence with a real LBM preflow restart and a real FSIDriver3D candidate run for `cap_2e-2_E_2e4`.",
        "",
        "The allowed claim is limited to a real solver run over the public tutorial time window compared against the Step107 public-plot digitization.",
        "",
        "## Result",
        "",
        f"- Real LBM preflow: {'pass' if preflow['preflow_pass'] else 'fail'}",
        f"- Real solver candidate: {'pass' if solver['real_solver_candidate_pass'] else 'fail'}",
        f"- Real monitor extraction: {'pass' if monitor['monitor_alignment_pass'] else 'fail'}",
        f"- Real monitor error comparison: {'pass' if error['step111_error_comparison_pass'] else 'fail'}",
        f"- Output guard: {'pass' if guard['output_guard_pass'] else 'fail'}",
        "",
        "## Artifacts",
        "",
        "- Preflow report: `outputs/step111_real_lbm_preflow/preflow_report.json`",
        "- LBM restart: `outputs/step111_real_lbm_preflow/lbm_preflow_restart.npz`",
        "- Solver report: `outputs/step111_real_solver_candidate/real_solver_candidate_report.json`",
        "- Monitor report: `outputs/step111_real_solver_candidate/monitor_definition_report.json`",
        "- Error report: `outputs/step111_error_comparison/error_report.json`",
        "- Guard report: `outputs/step111_output_guard/output_guard_report.json`",
        "- Artifact manifest: `outputs/step111_artifact_manifest/artifact_manifest.json`",
        "",
        "## Step112 Gate",
        "",
        "If the real candidate does not improve public-plot metrics enough for the next target, Step112 should repair structural dynamics or reaction transfer before expanding the candidate search.",
        "",
    ]
    report = "\n".join(lines)
    (ROOT / "STEP111_FLUENT_PUBLIC_PLOT_REAL_SOLVER_CANDIDATE_MATERIALIZATION_REPORT.md").write_text(report, encoding="utf-8")
    (ROOT / "docs" / "111_fluent_public_plot_real_solver_candidate_materialization.md").write_text(report, encoding="utf-8")


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step111_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {"extension": path.suffix.lower(), "path": rel, "size_bytes": int(path.stat().st_size), "step111_related": is_step111_related(rel)}


def is_step111_related(path: str) -> bool:
    lower = path.lower()
    return "step111" in lower or lower in {"docs/111_fluent_public_plot_real_solver_candidate_materialization.md"}


def is_official_file(row: dict, policy: dict) -> bool:
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(row["path"].lower()).name in names


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step111_", "logs/step111_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
