from __future__ import annotations

import csv
import json
import math
from pathlib import Path


STEP104_ROW_NAME = "fluent_duct_flap_setup_repair_48_5step_smoke"
ALLOWED_CLAIM = (
    "Fluent duct-flap problem setup repair is wired for a short proxy smoke, "
    "and the remaining Fluent-equivalence gaps are explicitly reported."
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


def rel_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))
