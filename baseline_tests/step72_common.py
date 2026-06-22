import csv
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def read_json(path):
    with resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_csv_rows(path, rows, fieldnames=None):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fieldnames or sorted({key for row in rows for key in row.keys()}))
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def write_log(relative_path, lines):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def run_named_audit(build_func, output_dir, log_path, pass_key, marker, stem):
    rows, summary = build_func(ROOT)
    if not summary[pass_key]:
        raise RuntimeError(f"{marker} failed: {summary}")
    out_dir = ROOT / output_dir
    write_csv_rows(out_dir / f"{stem}.csv", rows)
    write_csv_rows(out_dir / f"{stem}_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / f"{stem}.json", {"summary": summary, "rows": rows})
    write_log(log_path, [marker, f"row_count={summary.get('row_count', 0)}"])
    print(marker)
    return rows, summary
