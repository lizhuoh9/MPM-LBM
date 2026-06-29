from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


STEP = 153
DEFAULT_INPUT = Path("benchmarks") / "private" / "fluent_fsi_2way" / "outputs" / "raw_monitor_export.txt"
DEFAULT_OFFICIAL_MONITOR = (
    Path("benchmarks") / "private" / "fluent_fsi_2way" / "outputs" / "official_monitor.csv"
)
DEFAULT_OUTPUT_DIR = Path("outputs") / "step153_official_monitor_extract"

OUTPUT_FILES = [
    "official_monitor_extraction_summary.json",
    "official_monitor_schema_preview.json",
    "official_monitor_hash_report.json",
    "report.md",
]

NORMALIZED_COLUMNS = [
    "time_s",
    "flap_tip_total_displacement_m",
    "step",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
    "flap_tip_velocity_m_per_s",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
]


def _normalize_header(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[\[\]()/{}]", " ", normalized)
    normalized = normalized.replace("-", " ").replace("_", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


COLUMN_ALIASES = {
    "time_s": [
        "time_s",
        "time",
        "Time",
        "flow-time",
        "flow_time_s",
        "Flow Time",
    ],
    "flap_tip_total_displacement_m": [
        "flap_tip_total_displacement_m",
        "total_displacement",
        "Total Displacement",
        "displacement",
        "disp",
        "monitor_displacement_m",
    ],
    "flap_tip_x_displacement_m": [
        "flap_tip_x_displacement_m",
        "x_displacement",
        "X Displacement",
        "disp_x",
    ],
    "flap_tip_y_displacement_m": [
        "flap_tip_y_displacement_m",
        "y_displacement",
        "Y Displacement",
        "disp_y",
    ],
    "flap_tip_velocity_m_per_s": [
        "flap_tip_velocity_m_per_s",
        "velocity",
        "Velocity",
        "tip_velocity",
        "monitor_velocity_m_per_s",
    ],
    "fluid_force_magnitude_n": [
        "fluid_force_magnitude_n",
        "force_magnitude",
        "Force Magnitude",
        "force",
        "fluid_force",
    ],
    "fluid_force_x_n": [
        "fluid_force_x_n",
        "force_x",
        "X Force",
    ],
    "fluid_force_y_n": [
        "fluid_force_y_n",
        "force_y",
        "Y Force",
    ],
    "step": [
        "step",
        "Step",
        "timestep",
        "time_step",
    ],
}

ALIAS_TO_COLUMN = {
    _normalize_header(alias): column for column, aliases in COLUMN_ALIASES.items() for alias in aliases
}


def run_step153_official_monitor_extract_and_normalize(
    input_path: Path | str = DEFAULT_INPUT,
    official_monitor: Path | str = DEFAULT_OFFICIAL_MONITOR,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    input_path = Path(input_path)
    official_monitor = Path(official_monitor)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        _clear_known_outputs(output_dir)

    if not input_path.is_file():
        summary = _base_summary(
            input_path=input_path,
            official_monitor=official_monitor,
            status="waiting_for_official_monitor_source",
            reason="official_monitor_source_missing",
            schema_errors=["official monitor source is missing"],
            ready_for_step150=False,
            official_monitor_written_private=False,
            normalized_rows=[],
            columns=[],
            delimiter=None,
        )
        summary["next_action"] = "export_fluent_or_system_coupling_monitor"
        _write_all_outputs(output_dir, summary)
        return summary

    try:
        source = _read_source_table(input_path)
        normalized_rows, columns, schema_errors = _normalize_rows(source)
    except Exception as exc:
        source = {"delimiter": None, "rows": [], "headers": []}
        normalized_rows = []
        columns = []
        schema_errors = [f"source_parse_failed: {exc}"]

    if schema_errors:
        summary = _base_summary(
            input_path=input_path,
            official_monitor=official_monitor,
            status="official_monitor_source_invalid",
            reason="official_monitor_source_schema_invalid",
            schema_errors=schema_errors,
            ready_for_step150=False,
            official_monitor_written_private=False,
            normalized_rows=normalized_rows,
            columns=columns,
            delimiter=source.get("delimiter"),
            source_columns=source.get("headers", []),
        )
        _write_all_outputs(output_dir, summary)
        return summary

    _write_monitor_csv(official_monitor, normalized_rows, columns)
    hash_report = _official_hash_report(official_monitor)
    summary = _base_summary(
        input_path=input_path,
        official_monitor=official_monitor,
        status="official_monitor_ready_for_step150",
        reason="official_monitor_extracted_and_normalized",
        schema_errors=[],
        ready_for_step150=True,
        official_monitor_written_private=True,
        normalized_rows=normalized_rows,
        columns=columns,
        delimiter=source.get("delimiter"),
        source_columns=source.get("headers", []),
        hash_report=hash_report,
    )
    _write_all_outputs(output_dir, summary)
    return summary


def _read_source_table(path: Path) -> dict[str, Any]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not lines:
        return {"headers": [], "rows": [], "delimiter": None}

    header = lines[0]
    delimiter = _detect_delimiter(header)
    if delimiter in (",", "\t"):
        rows, headers = _read_delimited(path, delimiter)
    else:
        headers = re.split(r"\s+", header.strip())
        rows = []
        for line in lines[1:]:
            values = re.split(r"\s+", line.strip())
            if len(values) != len(headers):
                raise ValueError("space-delimited row width does not match header width")
            rows.append(dict(zip(headers, values)))
    return {"headers": headers, "rows": rows, "delimiter": delimiter}


def _read_delimited(path: Path, delimiter: str) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        headers = [] if reader.fieldnames is None else [header.strip() for header in reader.fieldnames]
        rows = []
        for row in reader:
            rows.append({str(key).strip(): value for key, value in row.items()})
    return rows, headers


def _detect_delimiter(header: str) -> str:
    if "," in header:
        return ","
    if "\t" in header:
        return "\t"
    return "whitespace"


def _normalize_rows(source: dict[str, Any]) -> tuple[list[dict[str, str]], list[str], list[str]]:
    rows = source["rows"]
    headers = source["headers"]
    errors: list[str] = []
    column_map = _column_map(headers)
    if "time_s" not in column_map:
        errors.append("missing required time_s column")
    if "flap_tip_total_displacement_m" not in column_map:
        errors.append("missing required displacement column")
    if not rows:
        errors.append("official monitor source has no data rows")
    if errors:
        return [], _normalized_output_columns(column_map), errors

    normalized_rows: list[dict[str, str]] = []
    previous_time = None
    for index, row in enumerate(rows):
        normalized: dict[str, str] = {}
        for output_column, source_column in column_map.items():
            raw_value = row.get(source_column, "")
            try:
                numeric = _parse_number(raw_value)
            except Exception:
                errors.append(f"{output_column} at row {index} is not finite")
                continue
            if output_column == "time_s":
                if previous_time is not None and numeric < previous_time:
                    errors.append("time_s must be monotonic non-decreasing")
                previous_time = numeric
            normalized[output_column] = _format_number(numeric)
        normalized_rows.append(normalized)

    columns = _normalized_output_columns(column_map)
    if errors:
        return [], columns, errors
    return normalized_rows, columns, []


def _column_map(headers: Sequence[str]) -> dict[str, str]:
    mapped = {}
    for header in headers:
        normalized = _normalize_header(header)
        output = ALIAS_TO_COLUMN.get(normalized)
        if output and output not in mapped:
            mapped[output] = header
    return mapped


def _normalized_output_columns(column_map: dict[str, str]) -> list[str]:
    return [column for column in NORMALIZED_COLUMNS if column in column_map]


def _parse_number(value: Any) -> float:
    text = str(value).strip()
    if text == "":
        raise ValueError("empty numeric value")
    number = float(text.replace(",", ""))
    if not math.isfinite(number):
        raise ValueError("non-finite numeric value")
    return number


def _format_number(value: float) -> str:
    return f"{value:.15g}"


def _base_summary(
    input_path: Path,
    official_monitor: Path,
    status: str,
    reason: str,
    schema_errors: list[str],
    ready_for_step150: bool,
    official_monitor_written_private: bool,
    normalized_rows: list[dict[str, str]],
    columns: list[str],
    delimiter: str | None,
    source_columns: Sequence[str] | None = None,
    hash_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    time_values = [float(row["time_s"]) for row in normalized_rows if "time_s" in row]
    hash_report = hash_report or _official_hash_report(official_monitor)
    return {
        "step": STEP,
        "status": status,
        "reason": reason,
        "input": _display_path(input_path),
        "input_exists": input_path.is_file(),
        "official_monitor_path": _display_path(official_monitor),
        "official_monitor_written_private": official_monitor_written_private,
        "official_monitor_committed": bool(hash_report.get("official_monitor_committed", False)),
        "official_monitor_hash": hash_report.get("official_monitor_hash"),
        "official_monitor_size_bytes": hash_report.get("size_bytes", 0),
        "ready_for_step150": ready_for_step150,
        "columns": columns,
        "source_columns": list(source_columns or []),
        "source_delimiter": delimiter,
        "row_count": len(normalized_rows),
        "time_start_s": min(time_values) if time_values else None,
        "time_end_s": max(time_values) if time_values else None,
        "schema_valid": ready_for_step150,
        "schema_errors": list(schema_errors),
        "sample_values_included": False,
        "fabricated_metrics_used": False,
        "step150_executed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_all_outputs(output_dir: Path, summary: dict[str, Any]) -> None:
    _write_json(output_dir / "official_monitor_extraction_summary.json", summary)
    _write_json(output_dir / "official_monitor_schema_preview.json", _schema_preview(summary))
    _write_json(output_dir / "official_monitor_hash_report.json", _hash_report_from_summary(summary))
    _write_report(output_dir, summary)


def _schema_preview(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": summary["status"],
        "input": summary["input"],
        "official_monitor_path": summary["official_monitor_path"],
        "ready_for_step150": summary["ready_for_step150"],
        "schema_valid": summary["schema_valid"],
        "schema_errors": summary["schema_errors"],
        "columns": summary["columns"],
        "source_columns": summary["source_columns"],
        "source_delimiter": summary["source_delimiter"],
        "row_count": summary["row_count"],
        "time_start_s": summary["time_start_s"],
        "time_end_s": summary["time_end_s"],
        "sample_values_included": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _hash_report_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": summary["status"],
        "official_monitor": summary["official_monitor_path"],
        "exists": bool(summary["official_monitor_hash"]),
        "official_monitor_hash": summary["official_monitor_hash"],
        "size_bytes": summary["official_monitor_size_bytes"],
        "official_monitor_committed": summary["official_monitor_committed"],
        "private_payload_committed": summary["official_monitor_committed"],
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_monitor_csv(path: Path, rows: Sequence[dict[str, str]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Step153 Official Monitor Extraction and Normalization",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Input exists: `{summary.get('input_exists')}`",
        f"- Official monitor written private: `{summary.get('official_monitor_written_private')}`",
        f"- Official monitor path: `{summary.get('official_monitor_path')}`",
        f"- Official monitor committed: `{summary.get('official_monitor_committed')}`",
        f"- Ready for Step150: `{summary.get('ready_for_step150')}`",
        f"- Row count: `{summary.get('row_count')}`",
        f"- Time range: `{summary.get('time_start_s')}` to `{summary.get('time_end_s')}`",
        f"- Columns: `{summary.get('columns')}`",
        f"- Step150 executed: `{summary.get('step150_executed')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "Step153 converts a private official Fluent/System Coupling monitor export into the private Step150 official monitor CSV.",
        "Committed Step153 artifacts contain only metadata, schema preview, and hash information, not private monitor row bodies.",
    ]
    errors = summary.get("schema_errors") or []
    if errors:
        lines.append("")
        lines.append("Schema errors:")
        for error in errors:
            lines.append(f"- {error}")
    if summary.get("next_action"):
        lines.append("")
        lines.append(f"Next action: `{summary['next_action']}`")
    text = "\n".join(lines) + "\n"
    (output_dir / "report.md").write_text(text, encoding="utf-8")
    if _is_default_output_dir(output_dir):
        doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "153" / "report.md"
        doc_report.parent.mkdir(parents=True, exist_ok=True)
        doc_report.write_text(text, encoding="utf-8")


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


def _clear_known_outputs(output_dir: Path) -> None:
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


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


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", dest="input_path", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", dest="official_monitor", type=Path, default=DEFAULT_OFFICIAL_MONITOR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step153_official_monitor_extract_and_normalize(
        input_path=args.input_path,
        official_monitor=args.official_monitor,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
