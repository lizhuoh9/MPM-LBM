import csv
import json
import os

import numpy as np


def make_all_fluid_geo(path, n_grid):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def save_json_config(config, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = config.to_dict() if hasattr(config, "to_dict") else dict(config)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def save_csv_rows(rows, path, fieldnames=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def assert_no_nan_inf_array(name, arr):
    values = np.asarray(arr)
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{name} contains NaN or Inf")


def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    return path
