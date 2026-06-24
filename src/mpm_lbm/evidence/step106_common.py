from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path


STEP106_DUCT_ROW_NAME = "duct_only_lbm_outlet_boundary_flow_48"
STEP106_FSI_ROW_NAME = "fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke"
ALLOWED_CLAIM = (
    "Fluent duct-flap proxy x-right pressure outlet flow propagation was repaired and demonstrated "
    "with gap-only proxy diagnostics; Fluent validation and direct quantitative equivalence remain forbidden."
)
FORBIDDEN_OFFICIAL_NAMES = {
    "fsi_2way.zip",
    "flap.msh",
    "steady_fluid_flow.jou",
    "flap_fsi_2way.cas.h5",
    "flap_fsi_2way.dat.h5",
}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_csv_rows(path: Path, rows: list[dict], fieldnames=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fieldnames or sorted({key for row in rows for key in row.keys()}))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def write_markdown_table(path: Path, title: str, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "| " + " | ".join(fieldnames) + " |", "| " + " | ".join("---" for _ in fieldnames) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fieldnames) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def numeric_values_finite(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True


def reset_output_dir(out_dir: Path, required_parent: Path) -> None:
    resolved_out = out_dir.resolve()
    resolved_parent = required_parent.resolve()
    if resolved_out == resolved_parent or resolved_parent not in resolved_out.parents:
        raise RuntimeError(f"refusing to reset unexpected Step106 output directory: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


def safe_ratio(numerator: float, denominator: float) -> float:
    if abs(float(denominator)) <= 1.0e-15:
        return 0.0
    return float(numerator) / float(denominator)
