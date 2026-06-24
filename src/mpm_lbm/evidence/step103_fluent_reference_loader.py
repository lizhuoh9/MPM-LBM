from __future__ import annotations

import csv
from pathlib import Path

from src.mpm_lbm.evidence.step103_common import read_json


def load_step103_fluent_reference_status(
    root: Path,
    schema_path: str = "configs/step103_fluent_reference_csv_schema.json",
) -> dict:
    root = Path(root)
    schema = read_json(root / schema_path)
    relative_csv_path = schema["optional_reference_csv_path"]
    csv_path = root / relative_csv_path
    if not csv_path.is_file():
        return {
            "fluent_reference_available": False,
            "fluent_reference_path": relative_csv_path,
            "fluent_reference_row_count": 0,
            "fluent_reference_schema_checked": True,
            "fluent_reference_schema_pass": False,
            "fluent_reference_columns": [],
            "fluent_reference_private_optional": True,
            "fluent_reference_committed": False,
        }

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        row_count = sum(1 for _ in reader)
    schema_pass = any(all(column in columns for column in group) for group in schema["required_columns_any"])
    return {
        "fluent_reference_available": True,
        "fluent_reference_path": relative_csv_path,
        "fluent_reference_row_count": int(row_count),
        "fluent_reference_schema_checked": True,
        "fluent_reference_schema_pass": bool(schema_pass and row_count > 0),
        "fluent_reference_columns": columns,
        "fluent_reference_private_optional": True,
        "fluent_reference_committed": False,
    }
