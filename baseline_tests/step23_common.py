import csv
import json
import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


STEP23_DRIVER_FIELDS = [
    "case",
    "geometry_type",
    "geometry_source",
    "quality_kind",
    "mode",
    "reaction_transfer_mode",
    "quality_check_enabled",
    "quality_check_strict",
    "quality_pass",
    "quality_severity",
    "quality_warnings_count",
    "quality_reasons_count",
    "quality_report_path",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
    "area_scale_final",
    "stable",
    "notes",
]


def make_quality_gated_config(base_config_path, out_config_path):
    with open(os.path.join(ROOT, base_config_path), "r", encoding="utf-8") as f:
        data = json.load(f)

    data["quality_check_enabled"] = True
    data["quality_check_strict"] = False
    data["write_vtk"] = False
    data["write_particles"] = False

    out_path = os.path.join(ROOT, out_config_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return data


def load_driver_config(relative_path):
    return FSIDriverConfig.from_json(os.path.join(ROOT, relative_path))


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_quality_gated_rows(rows, csv_path, npz_path):
    write_rows_csv_npz(rows, csv_path, npz_path, STEP23_DRIVER_FIELDS)


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for string_key in (
        "case",
        "geometry_type",
        "geometry_source",
        "quality_kind",
        "mode",
        "reaction_transfer_mode",
        "quality_pass",
        "quality_severity",
        "quality_report_path",
        "stable",
        "notes",
    ):
        if any(string_key in row for row in normalized):
            payload[string_key + "s"] = np.asarray([str(row.get(string_key, "")) for row in normalized])

    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(npz_path, **payload)


def enforce_quality_gated_config(config, config_path):
    if not config.quality_check_enabled:
        raise RuntimeError(f"{config_path} must set quality_check_enabled=true")
    if config.quality_check_strict:
        raise RuntimeError(f"{config_path} must set quality_check_strict=false for Step 23 scale validation")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable write_vtk and write_particles")


def run_quality_gated_config_paths(case, config_paths, out_dir, csv_name, npz_name):
    rows = []
    for relative_path in config_paths:
        config = load_driver_config(relative_path)
        row = run_quality_gated_driver_case(
            relative_path,
            case,
            config,
            os.path.join(out_dir, case_output_name(case, config)),
        )
        rows.append(row)
        print(
            f"case={case}, mode={row['mode']}, transfer={row['reaction_transfer_mode']}, "
            f"quality={row['quality_pass']}/{row['quality_severity']}, n_grid={row['n_grid']}, "
            f"rho=[{row['rho_min']:.9e}, {row['rho_max']:.9e}], "
            f"lbm_max_v={row['lbm_max_v']:.9e}, projected_mass={row['projected_mass']:.9e}, "
            f"stable={row['stable']}"
        )

    write_quality_gated_rows(rows, os.path.join(out_dir, csv_name), os.path.join(out_dir, npz_name))
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError(f"not all Step 23 rows are stable for {case}")
    return rows


def run_mixed_quality_gated_config_paths(case_config_paths, out_dir, csv_name, npz_name):
    rows = []
    for case, relative_path in case_config_paths:
        config = load_driver_config(relative_path)
        row = run_quality_gated_driver_case(
            relative_path,
            case,
            config,
            os.path.join(out_dir, case_output_name(case, config)),
        )
        rows.append(row)
        print(
            f"case={case}, mode={row['mode']}, transfer={row['reaction_transfer_mode']}, "
            f"quality={row['quality_pass']}/{row['quality_severity']}, n_grid={row['n_grid']}, "
            f"rho=[{row['rho_min']:.9e}, {row['rho_max']:.9e}], "
            f"lbm_max_v={row['lbm_max_v']:.9e}, projected_mass={row['projected_mass']:.9e}, "
            f"stable={row['stable']}"
        )

    write_quality_gated_rows(rows, os.path.join(out_dir, csv_name), os.path.join(out_dir, npz_name))
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError("not all Step 23 mixed driver rows are stable")
    return rows


def run_quality_gated_driver_case(config_path, case, config, out_dir):
    enforce_quality_gated_config(config, config_path)
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}/{config.coupling_mode}")

    report_path = os.path.join(out_dir, "geometry_quality_report.json")
    report_payload = collect_quality_report(out_dir)
    row = summarize_quality_gated_driver_case(case, config, diagnostics, driver, report_payload, report_path)
    assert_quality_gated_row_stable(row)
    return row


def collect_quality_report(out_dir):
    report_path = os.path.join(out_dir, "geometry_quality_report.json")
    if not os.path.isfile(report_path):
        raise RuntimeError(f"missing geometry_quality_report.json under {out_dir}")
    with open(report_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    if "report" not in payload or "gate" not in payload:
        raise RuntimeError(f"invalid quality report payload: {report_path}")
    return payload


def summarize_quality_gated_driver_case(case, config, diagnostics, driver, quality_payload, report_path):
    gate = quality_payload["gate"]
    report = quality_payload["report"]
    area_scale_final = 1.0
    if driver.link_area_coupler is not None:
        area_scale_final = float(driver.link_area_coupler.get_stats()["area_scale"])

    row = {
        "case": case,
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path or config.geometry_type,
        "quality_kind": report.get("quality_kind", ""),
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "quality_check_enabled": bool(config.quality_check_enabled),
        "quality_check_strict": bool(config.quality_check_strict),
        "quality_pass": bool(gate["pass"]),
        "quality_severity": gate["severity"],
        "quality_warnings_count": len(gate.get("warnings", [])),
        "quality_reasons_count": len(gate.get("reasons", [])),
        "quality_report_path": _relative_path(report_path),
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": max(int(row["step"]) for row in diagnostics),
        "total_mpm_substeps": max(int(row["total_mpm_substeps"]) for row in diagnostics),
        "rho_min": min(float(row["rho_min"]) for row in diagnostics),
        "rho_max": max(float(row["rho_max"]) for row in diagnostics),
        "lbm_max_v": max(float(row["lbm_max_v"]) for row in diagnostics),
        "mpm_min_J": min(float(row["mpm_min_J"]) for row in diagnostics),
        "mpm_max_speed": max(float(row["mpm_max_speed"]) for row in diagnostics),
        "projected_mass": max(float(row["projected_mass"]) for row in diagnostics),
        "active_cell_count": max(int(row["active_cell_count"]) for row in diagnostics),
        "cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in diagnostics),
        "hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in diagnostics),
        "bb_link_count": max(int(row["bb_link_count"]) for row in diagnostics),
        "active_reaction_particle_count": max(int(row["active_reaction_particle_count"]) for row in diagnostics),
        "area_scale_final": area_scale_final,
        "stable": True,
        "notes": "Step 23 quality-gated synthetic imported geometry validation; no new FSI physics",
    }
    return row


def assert_quality_gated_row_stable(row):
    _assert_row_finite(
        row,
        excluded=(
            "case",
            "geometry_type",
            "geometry_source",
            "quality_kind",
            "mode",
            "reaction_transfer_mode",
            "quality_check_enabled",
            "quality_check_strict",
            "quality_pass",
            "quality_severity",
            "quality_report_path",
            "stable",
            "notes",
        ),
    )
    if not _as_bool(row["stable"]):
        raise RuntimeError(f"unstable Step 23 driver row: {row}")
    if not _as_bool(row["quality_check_enabled"]):
        raise RuntimeError(f"quality check must be enabled: {row}")
    if _as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"quality_check_strict must remain false: {row}")
    if not _as_bool(row["quality_pass"]):
        raise RuntimeError(f"quality gate failed unexpectedly: {row}")
    if row["quality_severity"] not in {"ok", "warning"}:
        raise RuntimeError(f"unexpected quality severity: {row}")
    if int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"quality gate reported reasons: {row}")
    if int(row["n_grid"]) == 48 and int(row["completed_lbm_steps"]) < 10:
        raise RuntimeError(f"48^3 row did not complete enough steps: {row}")
    if int(row["n_grid"]) == 64 and int(row["completed_lbm_steps"]) < 5:
        raise RuntimeError(f"64^3 row did not complete enough steps: {row}")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError(f"rho outside accepted range: {row}")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v exceeded accepted range: {row}")
    if float(row["mpm_min_J"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J became non-positive: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")
    if row["mode"] == "none" and float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("none row must keep cell_force at zero")
    if row["mode"] == "penalty" and float(row["cell_force_max_norm"]) <= 0.0:
        raise RuntimeError("penalty row must produce positive cell_force")
    if row["mode"] == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary row must keep cell_force at zero")
        if int(row["bb_link_count"]) <= 0:
            raise RuntimeError("moving_boundary row must record bounce-back links")
    if row["reaction_transfer_mode"] == "link_area_experimental" and not np.isfinite(float(row["area_scale_final"])):
        raise RuntimeError("link_area_experimental row must record finite area_scale_final")
    if not os.path.isfile(os.path.join(ROOT, row["quality_report_path"])):
        raise RuntimeError(f"missing quality report path: {row['quality_report_path']}")


def case_output_name(case, config):
    return f"{case}_{config.n_grid}_{config.coupling_mode}_{config.reaction_transfer_mode}"


def _assert_row_finite(row, excluded=()):
    values = []
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        values.append(float(value))
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"row contains NaN or Inf: {row}")


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _relative_path(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")
