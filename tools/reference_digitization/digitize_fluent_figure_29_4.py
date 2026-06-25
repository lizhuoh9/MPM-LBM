from __future__ import annotations

import csv
import json
from pathlib import Path


def main(config_path: str, output_path: str) -> None:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    bbox = config["plot_bbox_pixels"]
    x_range = config["x_range"]
    y_range = config["y_range"]
    rows = []
    for point in config["curve_points_pixels"]:
        time_s = map_linear(point["x"], bbox["x_min"], bbox["x_max"], x_range[0], x_range[1])
        displacement_m = map_linear(point["y"], bbox["y_max"], bbox["y_min"], y_range[0], y_range[1])
        rows.append(
            {
                "digitization_method": "manual_pixel_calibration",
                "digitization_uncertainty_m": config.get("digitization_uncertainty_m", 2.5e-5),
                "fluent_public_digitized_total_displacement_m": max(0.0, displacement_m),
                "source_figure": "Figure 29.4",
                "time_s": time_s,
            }
        )
    write_csv(Path(output_path), rows)


def map_linear(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if src_max == src_min:
        raise ValueError("source range must be nonzero")
    alpha = (float(value) - float(src_min)) / (float(src_max) - float(src_min))
    return float(dst_min) + alpha * (float(dst_max) - float(dst_min))


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "time_s",
        "fluent_public_digitized_total_displacement_m",
        "digitization_uncertainty_m",
        "source_figure",
        "digitization_method",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Map manually sampled Figure 29.4 pixels to data coordinates.")
    parser.add_argument("config_path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    main(args.config_path, args.output_path)
