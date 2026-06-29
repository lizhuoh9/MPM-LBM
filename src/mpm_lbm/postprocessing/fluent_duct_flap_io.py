from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_repo_path(path: Path | str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root() / candidate


def display_path(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(repo_root()))
    except ValueError:
        return str(candidate)


def require_file(path: Path | str, label: str) -> Path:
    resolved = resolve_repo_path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"missing required {label}: {display_path(resolved)}")
    return resolved


def read_json(path: Path | str) -> dict[str, Any]:
    with require_file(path, "json").open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_csv_rows(path: Path | str) -> list[dict[str, str]]:
    with require_file(path, "csv").open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path | str, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def load_npz(path: Path | str) -> dict[str, np.ndarray]:
    with np.load(require_file(path, "npz")) as data:
        return {name: data[name] for name in data.files}


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value
