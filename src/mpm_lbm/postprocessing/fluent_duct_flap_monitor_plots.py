from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .fluent_duct_flap_io import display_path, parse_bool, parse_float, read_csv_rows


def load_csv_rows(path: Path) -> list[dict]:
    return list(read_csv_rows(path))


def write_monitor_displacement_plot(solver_monitor_csv: Path, output_path: Path) -> dict[str, Any]:
    rows = load_csv_rows(solver_monitor_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    times = [parse_float(row.get("time_s")) for row in rows]
    series = {
        "flap_tip_total_displacement_m": [
            parse_float(row.get("flap_tip_total_displacement_m")) for row in rows
        ],
        "official_point_like_total_displacement_m": [
            parse_float(row.get("official_point_like_total_displacement_m")) for row in rows
        ],
    }

    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=160)
    plotted = []
    for name, values in series.items():
        if values and any(value != 0.0 for value in values):
            ax.plot(times, values, label=name)
            plotted.append(name)
        elif values:
            ax.plot(times, values, label=name)
            plotted.append(name)
    ax.set_title("Step155 proxy monitor displacement; not official Fluent monitor")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("displacement [m]")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return {
        "status": "monitor_displacement_plot_written",
        "path": display_path(output_path),
        "row_count": len(rows),
        "series_plotted": plotted,
        "validation_claim_allowed": False,
    }


def write_force_monitor_plot(solver_force_monitor_csv: Path, output_path: Path) -> dict[str, Any]:
    rows = load_csv_rows(solver_force_monitor_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    times = [parse_float(row.get("time_s")) for row in rows]
    force = [parse_float(row.get("fluid_force_magnitude_n")) for row in rows]

    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=160)
    ax.plot(times, force, color="#e45756", label="fluid_force_magnitude_n")
    ax.set_title("Step155 force proxy; not direct Fluent wall integral")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("force proxy [N]")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return {
        "status": "force_monitor_plot_written",
        "path": display_path(output_path),
        "row_count": len(rows),
        "force_is_direct_fluent_wall_integral": _force_is_direct_fluent_wall_integral(rows),
        "validation_claim_allowed": False,
    }


def summarize_monitor_rows(solver_monitor_csv: Path, solver_force_csv: Path) -> dict[str, Any]:
    monitor_rows = load_csv_rows(solver_monitor_csv)
    force_rows = load_csv_rows(solver_force_csv)
    return {
        "step": 156,
        "status": "monitor_plot_report_written",
        "solver_monitor_rows": len(monitor_rows),
        "solver_force_monitor_rows": len(force_rows),
        "monitor_displacement_plot_written": True,
        "force_monitor_plot_written": True,
        "force_is_direct_fluent_wall_integral": _force_is_direct_fluent_wall_integral(force_rows),
        "validation_claim_allowed": False,
    }


def _force_is_direct_fluent_wall_integral(rows: list[dict]) -> bool:
    for row in rows:
        if "force_is_direct_fluent_wall_integral" in row:
            return parse_bool(row["force_is_direct_fluent_wall_integral"])
    return False
