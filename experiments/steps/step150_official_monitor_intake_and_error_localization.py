from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step149_fluent_official_vs_our_solver_error_localization import (
    ALIGNED_FIELDS,
    DISPLACEMENT_ALIASES,
    FORCE_ALIASES,
    run_step149_error_localization,
)


STEP = 150
DEFAULT_OFFICIAL_MONITOR = Path("benchmarks") / "private" / "fluent_fsi_2way" / "outputs" / "official_monitor.csv"
DEFAULT_SOLVER_MONITOR = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_monitor.csv"
DEFAULT_SOLVER_FORCE_MONITOR = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_force_monitor.csv"
DEFAULT_SOLVER_SUMMARY = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_reproduction_summary.json"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step150_official_monitor_error_localization"

OUTPUT_FILES = [
    "official_monitor_intake_summary.json",
    "official_monitor_schema_report.json",
    "official_monitor_private_hash_report.json",
    "aligned_monitor_comparison.csv",
    "displacement_error_metrics.json",
    "force_error_metrics.json",
    "phase_lag_metrics.json",
    "solver_bug_hypotheses.json",
    "error_localization_summary.json",
    "step150_decision_summary.json",
    "report.md",
]


def run_step150_official_monitor_intake(
    official_monitor: Path | str = DEFAULT_OFFICIAL_MONITOR,
    solver_monitor: Path | str = DEFAULT_SOLVER_MONITOR,
    solver_force_monitor: Path | str = DEFAULT_SOLVER_FORCE_MONITOR,
    solver_summary: Path | str | None = DEFAULT_SOLVER_SUMMARY,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    official_monitor = Path(official_monitor)
    solver_monitor = Path(solver_monitor)
    solver_force_monitor = Path(solver_force_monitor)
    solver_summary_path = None if solver_summary is None else Path(solver_summary)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        _clear_known_outputs(output_dir)

    hash_report = _official_hash_report(official_monitor)
    _write_json(output_dir / "official_monitor_private_hash_report.json", hash_report)

    if not official_monitor.is_file():
        schema_report = _schema_report_missing(official_monitor)
        _write_json(output_dir / "official_monitor_schema_report.json", schema_report)
        solver_report = _solver_monitor_report(solver_monitor) if solver_monitor.is_file() else None
        return _write_blocked_outputs(
            output_dir,
            status="missing_official_monitor",
            reason="official_reference_missing",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
            hash_report=hash_report,
            schema_report=schema_report,
            solver_report=solver_report,
        )

    schema_report = _official_schema_report(official_monitor)
    _write_json(output_dir / "official_monitor_schema_report.json", schema_report)

    if not solver_monitor.is_file():
        return _write_blocked_outputs(
            output_dir,
            status="missing_solver_monitor",
            reason="solver_monitor_missing",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
            hash_report=hash_report,
            schema_report=schema_report,
        )

    solver_report = _solver_monitor_report(solver_monitor)
    if not schema_report["schema_valid"]:
        return _write_blocked_outputs(
            output_dir,
            status="schema_invalid",
            reason="official_monitor_schema_invalid",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
            hash_report=hash_report,
            schema_report=schema_report,
            solver_report=solver_report,
        )

    if not solver_report["solver_monitor_valid"]:
        return _write_blocked_outputs(
            output_dir,
            status="missing_solver_monitor",
            reason="solver_monitor_invalid",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
            hash_report=hash_report,
            schema_report=schema_report,
            solver_report=solver_report,
        )

    if not _time_ranges_overlap(schema_report, solver_report):
        return _write_blocked_outputs(
            output_dir,
            status="no_time_overlap",
            reason="official_solver_time_ranges_do_not_overlap",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
            hash_report=hash_report,
            schema_report=schema_report,
            solver_report=solver_report,
        )

    step149_summary = run_step149_error_localization(
        official_monitor=official_monitor,
        solver_monitor=solver_monitor,
        solver_force_monitor=solver_force_monitor,
        solver_summary=solver_summary_path,
        output_dir=output_dir,
        force=True,
    )
    hypotheses = _read_json(output_dir / "solver_bug_hypotheses.json")
    hypotheses["next_fix_step_recommended"] = 151
    hypotheses["step150_intake_verified"] = True
    _write_json(output_dir / "solver_bug_hypotheses.json", hypotheses)

    aligned_count = _csv_row_count(output_dir / "aligned_monitor_comparison.csv")
    summary = _success_summary(
        official_monitor=official_monitor,
        solver_monitor=solver_monitor,
        solver_force_monitor=solver_force_monitor,
        solver_summary_path=solver_summary_path,
        hash_report=hash_report,
        schema_report=schema_report,
        solver_report=solver_report,
        step149_summary=step149_summary,
        hypotheses=hypotheses,
        aligned_count=aligned_count,
    )
    _write_json(output_dir / "official_monitor_intake_summary.json", summary)
    _write_json(output_dir / "error_localization_summary.json", summary)
    _write_json(output_dir / "step150_decision_summary.json", summary)
    _write_report(output_dir, summary)
    return summary


def _write_blocked_outputs(
    output_dir: Path,
    status: str,
    reason: str,
    official_monitor: Path,
    solver_monitor: Path,
    solver_force_monitor: Path,
    solver_summary_path: Path | None,
    hash_report: dict[str, Any],
    schema_report: dict[str, Any],
    solver_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    solver_loaded = bool(solver_monitor.is_file())
    summary = {
        "step": STEP,
        "status": status,
        "reason": reason,
        "official_monitor": _display_path(official_monitor),
        "solver_monitor": _display_path(solver_monitor),
        "solver_force_monitor": _display_path(solver_force_monitor),
        "solver_summary": None if solver_summary_path is None else _display_path(solver_summary_path),
        "official_reference_loaded": bool(official_monitor.is_file()),
        "solver_monitor_loaded": solver_loaded,
        "official_monitor_hash": hash_report.get("official_monitor_hash"),
        "official_monitor_rows": schema_report.get("row_count", 0),
        "official_monitor_committed": bool(hash_report.get("official_monitor_committed", False)),
        "official_time_start_s": schema_report.get("time_start_s"),
        "official_time_end_s": schema_report.get("time_end_s"),
        "schema_valid": bool(schema_report.get("schema_valid", False)),
        "schema_errors": list(schema_report.get("schema_errors", [])),
        "solver_monitor_rows": None if solver_report is None else solver_report.get("row_count", 0),
        "solver_time_start_s": None if solver_report is None else solver_report.get("time_start_s"),
        "solver_time_end_s": None if solver_report is None else solver_report.get("time_end_s"),
        "aligned_sample_count": 0,
        "step149_comparison_ran": False,
        "error_metrics_present": False,
        "solver_bug_hypotheses_present": False,
        "top_bug_category": None,
        "next_code_fix_step_identified": False,
        "recommended_next_step": None,
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_json(output_dir / "official_monitor_intake_summary.json", summary)
    _write_csv(output_dir / "aligned_monitor_comparison.csv", [], ALIGNED_FIELDS)
    for name in ("displacement_error_metrics.json", "force_error_metrics.json", "phase_lag_metrics.json"):
        _write_json(output_dir / name, {"status": status, "reason": reason})
    _write_json(
        output_dir / "solver_bug_hypotheses.json",
        {
            "status": status,
            "hypotheses": [],
            "next_fix_step_recommended": None,
            "fabricated_metrics_used": False,
        },
    )
    _write_json(output_dir / "error_localization_summary.json", summary)
    _write_json(output_dir / "step150_decision_summary.json", summary)
    _write_report(output_dir, summary)
    return summary


def _success_summary(
    official_monitor: Path,
    solver_monitor: Path,
    solver_force_monitor: Path,
    solver_summary_path: Path | None,
    hash_report: dict[str, Any],
    schema_report: dict[str, Any],
    solver_report: dict[str, Any],
    step149_summary: dict[str, Any],
    hypotheses: dict[str, Any],
    aligned_count: int,
) -> dict[str, Any]:
    top_category = hypotheses.get("top_category")
    hypotheses_present = bool(hypotheses.get("hypotheses"))
    return {
        "step": STEP,
        "status": "error_localization_complete",
        "step149_status": step149_summary.get("status"),
        "official_monitor": _display_path(official_monitor),
        "solver_monitor": _display_path(solver_monitor),
        "solver_force_monitor": _display_path(solver_force_monitor),
        "solver_summary": None if solver_summary_path is None else _display_path(solver_summary_path),
        "official_reference_loaded": True,
        "solver_monitor_loaded": True,
        "official_monitor_hash": hash_report["official_monitor_hash"],
        "official_monitor_size_bytes": hash_report["size_bytes"],
        "official_monitor_rows": schema_report["row_count"],
        "official_monitor_columns": schema_report["columns"],
        "official_monitor_committed": bool(hash_report["official_monitor_committed"]),
        "official_time_start_s": schema_report["time_start_s"],
        "official_time_end_s": schema_report["time_end_s"],
        "official_displacement_column": schema_report["displacement_column"],
        "official_force_column": schema_report["force_column"],
        "schema_valid": True,
        "schema_errors": [],
        "solver_monitor_rows": solver_report["row_count"],
        "solver_time_start_s": solver_report["time_start_s"],
        "solver_time_end_s": solver_report["time_end_s"],
        "aligned_sample_count": aligned_count,
        "step149_comparison_ran": True,
        "error_metrics_present": bool(step149_summary.get("error_metrics_present", False)),
        "solver_bug_hypotheses_present": hypotheses_present,
        "top_bug_category": top_category,
        "next_code_fix_step_identified": hypotheses_present,
        "recommended_next_step": 151 if hypotheses_present else None,
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _official_hash_report(path: Path) -> dict[str, Any]:
    report = {
        "step": STEP,
        "official_monitor": _display_path(path),
        "exists": path.is_file(),
        "official_monitor_hash": None,
        "size_bytes": 0,
        "official_monitor_committed": False,
        "private_payload_committed": False,
    }
    if path.is_file():
        report["official_monitor_hash"] = sha256(path.read_bytes()).hexdigest()
        report["size_bytes"] = path.stat().st_size
        report["official_monitor_committed"] = _git_tracks(path)
        report["private_payload_committed"] = bool(report["official_monitor_committed"])
    return report


def _schema_report_missing(path: Path) -> dict[str, Any]:
    return {
        "step": STEP,
        "official_monitor": _display_path(path),
        "schema_valid": False,
        "schema_errors": ["official monitor is missing"],
        "columns": [],
        "row_count": 0,
        "time_start_s": None,
        "time_end_s": None,
        "displacement_column": None,
        "force_column": None,
    }


def _official_schema_report(path: Path) -> dict[str, Any]:
    rows, columns = _read_csv_with_columns(path)
    errors: list[str] = []
    time_values: list[float] = []
    displacement_column = _find_column(columns, DISPLACEMENT_ALIASES)
    force_column = _find_column(columns, FORCE_ALIASES)

    if "time_s" not in columns:
        errors.append("missing required time_s column")
    if displacement_column is None:
        errors.append("missing required displacement column")
    if not rows:
        errors.append("official monitor has no data rows")

    if "time_s" in columns:
        previous = None
        for index, row in enumerate(rows):
            try:
                value = float(row["time_s"])
            except Exception:
                errors.append(f"time_s at row {index} is not finite")
                continue
            if not math.isfinite(value):
                errors.append(f"time_s at row {index} is not finite")
                continue
            if previous is not None and value < previous:
                errors.append("time_s must be monotonic non-decreasing")
                break
            previous = value
            time_values.append(value)

    if displacement_column is not None:
        for index, row in enumerate(rows):
            try:
                value = float(row[displacement_column])
            except Exception:
                errors.append(f"displacement at row {index} is not finite")
                break
            if not math.isfinite(value):
                errors.append(f"displacement at row {index} is not finite")
                break

    return {
        "step": STEP,
        "official_monitor": _display_path(path),
        "schema_valid": not errors,
        "schema_errors": errors,
        "columns": columns,
        "row_count": len(rows),
        "time_start_s": min(time_values) if time_values else None,
        "time_end_s": max(time_values) if time_values else None,
        "time_monotonic_non_decreasing": "time_s must be monotonic non-decreasing" not in errors,
        "displacement_column": displacement_column,
        "force_column": force_column,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _solver_monitor_report(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "solver_monitor": _display_path(path),
            "solver_monitor_valid": False,
            "row_count": 0,
            "time_start_s": None,
            "time_end_s": None,
        }
    rows, columns = _read_csv_with_columns(path)
    times = []
    for row in rows:
        try:
            value = float(row["time_s"])
        except Exception:
            continue
        if math.isfinite(value):
            times.append(value)
    return {
        "solver_monitor": _display_path(path),
        "solver_monitor_valid": bool(rows and "time_s" in columns and times),
        "row_count": len(rows),
        "time_start_s": min(times) if times else None,
        "time_end_s": max(times) if times else None,
    }


def _time_ranges_overlap(official_report: dict[str, Any], solver_report: dict[str, Any]) -> bool:
    official_start = official_report.get("time_start_s")
    official_end = official_report.get("time_end_s")
    solver_start = solver_report.get("time_start_s")
    solver_end = solver_report.get("time_end_s")
    if None in (official_start, official_end, solver_start, solver_end):
        return False
    return max(float(official_start), float(solver_start)) <= min(float(official_end), float(solver_end))


def _read_csv_with_columns(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = [] if reader.fieldnames is None else list(reader.fieldnames)
        return list(reader), columns


def _find_column(columns: Sequence[str], aliases: Sequence[str]) -> str | None:
    for alias in aliases:
        if alias in columns:
            return alias
    return None


def _clear_known_outputs(output_dir: Path) -> None:
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()


def _write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Step150 Fluent Official Monitor Intake and Real Error Localization",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Official reference loaded: `{summary.get('official_reference_loaded')}`",
        f"- Solver monitor loaded: `{summary.get('solver_monitor_loaded')}`",
        f"- Official monitor rows: `{summary.get('official_monitor_rows')}`",
        f"- Official time range: `{summary.get('official_time_start_s')}` to `{summary.get('official_time_end_s')}`",
        f"- Official monitor hash: `{summary.get('official_monitor_hash')}`",
        f"- Official monitor committed: `{summary.get('official_monitor_committed')}`",
        f"- Schema valid: `{summary.get('schema_valid')}`",
        f"- Solver monitor rows: `{summary.get('solver_monitor_rows')}`",
        f"- Solver time range: `{summary.get('solver_time_start_s')}` to `{summary.get('solver_time_end_s')}`",
        f"- Step149 comparison ran: `{summary.get('step149_comparison_ran')}`",
        f"- Aligned sample count: `{summary.get('aligned_sample_count')}`",
        f"- Error metrics present: `{summary.get('error_metrics_present')}`",
        f"- Solver bug hypotheses present: `{summary.get('solver_bug_hypotheses_present')}`",
        f"- Top bug category: `{summary.get('top_bug_category')}`",
        f"- Recommended next step: `{summary.get('recommended_next_step')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "Step150 validates the private official monitor intake and only runs Step149 comparison when the official and solver monitors are usable.",
        "Private official CSV contents are not copied into committed artifacts; only metadata and hash are recorded.",
    ]
    schema_errors = summary.get("schema_errors") or []
    if schema_errors:
        lines.append("")
        lines.append("Schema errors:")
        for error in schema_errors:
            lines.append(f"- {error}")
    output_report = output_dir / "report.md"
    output_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if _is_default_output_dir(output_dir):
        doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "150" / "report.md"
        doc_report.parent.mkdir(parents=True, exist_ok=True)
        doc_report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _csv_row_count(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open("r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _git_tracks(path: Path) -> bool:
    try:
        display = _display_path(path)
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "--error-unmatch", display],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def _display_path(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-monitor", type=Path, default=DEFAULT_OFFICIAL_MONITOR)
    parser.add_argument("--solver-monitor", type=Path, default=DEFAULT_SOLVER_MONITOR)
    parser.add_argument("--solver-force-monitor", type=Path, default=DEFAULT_SOLVER_FORCE_MONITOR)
    parser.add_argument("--solver-summary", type=Path, default=DEFAULT_SOLVER_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step150_official_monitor_intake(
        official_monitor=args.official_monitor,
        solver_monitor=args.solver_monitor,
        solver_force_monitor=args.solver_force_monitor,
        solver_summary=args.solver_summary,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
