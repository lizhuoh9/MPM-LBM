import csv
import json
import math
import os
from pathlib import Path

from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.squid_proxy.region_config import SquidProxyRegionConfig, load_squid_proxy_region_config


SEMANTIC_OVERLAP_NOTE = "region projection is semantic context, not a mass partition"
SCOPE_NOTE = (
    "Step 31 controlled squid proxy region projection and static driver smoke; "
    "no actuation, no swimming, and no new FSI physics"
)

ALIGNMENT_FIELDS = [
    "case",
    "candidate_id",
    "mode",
    "reaction_transfer_mode",
    "grid_size",
    "driver_projected_mass",
    "region_context_projected_mass_total",
    "mass_delta",
    "driver_active_cell_count",
    "region_context_active_cell_count_total",
    "active_cell_delta",
    "mantle_outer_projected_mass",
    "mantle_cavity_proxy_projected_mass",
    "funnel_outlet_proxy_projected_mass",
    "alignment_pass",
    "semantic_overlap_note",
    "scope_note",
]

ENGINEERING_LINK_AREA_FIELDS = [
    "candidate_id",
    "n_grid",
    "engineering_case",
    "link_area_case",
    "rho_min_delta",
    "rho_max_delta",
    "lbm_max_v_delta",
    "mpm_min_J_delta",
    "projected_mass_delta",
    "active_cell_count_delta",
    "hydro_force_max_norm_delta",
    "bb_link_count_max_delta",
    "active_reaction_particle_count_max_delta",
    "link_area_area_scale_final",
    "link_area_raw_area_scale_final",
    "comparison_pass",
    "scope_note",
]


def load_region_driver_context(geometry_config_path, region_config_path) -> tuple[GeometryConfig, SquidProxyRegionConfig]:
    geometry_config = GeometryConfig.from_json(_resolve_path(geometry_config_path))
    region_config = load_squid_proxy_region_config(_resolve_path(region_config_path))
    return geometry_config, region_config


def summarize_region_projection_alignment(region_projection_rows: list[dict], driver_rows: list[dict]) -> list[dict]:
    rows = []
    for driver_row in driver_rows:
        rows.append(summarize_static_driver_region_context(driver_row, region_projection_rows))
    return rows


def summarize_static_driver_region_context(driver_row: dict, projection_rows: list[dict]) -> dict:
    grid_size = int(float(driver_row["n_grid"]))
    region_rows = [row for row in projection_rows if int(float(row["grid_size"])) == grid_size]
    by_region = {row["region_id"]: row for row in region_rows}
    driver_mass = float(driver_row["projected_mass"])
    region_mass = sum(float(row["projected_mass"]) for row in region_rows)
    driver_active = int(float(driver_row["active_cell_count"]))
    region_active = sum(int(float(row["active_cell_count"])) for row in region_rows)
    row = {
        "case": driver_row.get("case", ""),
        "candidate_id": driver_row.get("candidate_id", "squid_proxy_region"),
        "mode": driver_row["mode"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "grid_size": grid_size,
        "driver_projected_mass": driver_mass,
        "region_context_projected_mass_total": region_mass,
        "mass_delta": driver_mass - region_mass,
        "driver_active_cell_count": driver_active,
        "region_context_active_cell_count_total": region_active,
        "active_cell_delta": driver_active - region_active,
        "mantle_outer_projected_mass": _region_mass(by_region, "mantle_outer"),
        "mantle_cavity_proxy_projected_mass": _region_mass(by_region, "mantle_cavity_proxy"),
        "funnel_outlet_proxy_projected_mass": _region_mass(by_region, "funnel_outlet_proxy"),
        "semantic_overlap_note": SEMANTIC_OVERLAP_NOTE,
        "scope_note": SCOPE_NOTE,
    }
    row["alignment_pass"] = bool(
        len(region_rows) == 7
        and driver_mass > 0.0
        and region_mass > 0.0
        and driver_active > 0
        and region_active > 0
        and row["mantle_outer_projected_mass"] > 0.0
        and row["mantle_cavity_proxy_projected_mass"] > 0.0
        and row["funnel_outlet_proxy_projected_mass"] > 0.0
        and SEMANTIC_OVERLAP_NOTE in row["semantic_overlap_note"]
        and _finite_values(row, excluded=("case", "candidate_id", "mode", "reaction_transfer_mode", "alignment_pass", "semantic_overlap_note", "scope_note"))
    )
    return row


def summarize_alignment_rows(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row["alignment_pass"])),
        "min_driver_projected_mass": min(float(row["driver_projected_mass"]) for row in rows) if rows else 0.0,
        "min_region_context_projected_mass_total": min(float(row["region_context_projected_mass_total"]) for row in rows) if rows else 0.0,
        "min_driver_active_cell_count": min(int(float(row["driver_active_cell_count"])) for row in rows) if rows else 0,
        "min_region_context_active_cell_count_total": min(int(float(row["region_context_active_cell_count_total"])) for row in rows) if rows else 0,
        "semantic_overlap_note": SEMANTIC_OVERLAP_NOTE,
        "scope_note": SCOPE_NOTE,
    }


def assert_alignment_summary(summary: dict) -> None:
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 31 region-driver alignment must have four passing rows: {summary}")
    if float(summary["min_driver_projected_mass"]) <= 0.0:
        raise RuntimeError(f"Step 31 driver projected mass must be positive: {summary}")
    if float(summary["min_region_context_projected_mass_total"]) <= 0.0:
        raise RuntimeError(f"Step 31 region projected mass context must be positive: {summary}")
    if int(summary["min_driver_active_cell_count"]) <= 0 or int(summary["min_region_context_active_cell_count_total"]) <= 0:
        raise RuntimeError(f"Step 31 region-driver active cell context must be positive: {summary}")
    if SEMANTIC_OVERLAP_NOTE not in str(summary["semantic_overlap_note"]):
        raise RuntimeError(f"Step 31 semantic overlap note is missing: {summary}")


def compare_engineering_vs_link_area_static(driver_rows: list[dict]) -> list[dict]:
    engineering = _single_driver_row(driver_rows, "moving_boundary", "engineering")
    link_area = _single_driver_row(driver_rows, "moving_boundary", "link_area_experimental")
    row = {
        "candidate_id": "squid_proxy_region",
        "n_grid": int(float(engineering["n_grid"])),
        "engineering_case": engineering.get("case", ""),
        "link_area_case": link_area.get("case", ""),
        "rho_min_delta": float(link_area["rho_min_global"]) - float(engineering["rho_min_global"]),
        "rho_max_delta": float(link_area["rho_max_global"]) - float(engineering["rho_max_global"]),
        "lbm_max_v_delta": float(link_area["lbm_max_v_global"]) - float(engineering["lbm_max_v_global"]),
        "mpm_min_J_delta": float(link_area["mpm_min_J_global"]) - float(engineering["mpm_min_J_global"]),
        "projected_mass_delta": float(link_area["projected_mass"]) - float(engineering["projected_mass"]),
        "active_cell_count_delta": int(float(link_area["active_cell_count"])) - int(float(engineering["active_cell_count"])),
        "hydro_force_max_norm_delta": float(link_area["hydro_force_max_norm"]) - float(engineering["hydro_force_max_norm"]),
        "bb_link_count_max_delta": int(float(link_area["bb_link_count_max"])) - int(float(engineering["bb_link_count_max"])),
        "active_reaction_particle_count_max_delta": int(float(link_area["active_reaction_particle_count_max"]))
        - int(float(engineering["active_reaction_particle_count_max"])),
        "link_area_area_scale_final": float(link_area["area_scale_final"]),
        "link_area_raw_area_scale_final": float(link_area["raw_area_scale_final"]),
        "scope_note": SCOPE_NOTE,
    }
    row["comparison_pass"] = bool(
        _as_bool(engineering["stable"])
        and _as_bool(link_area["stable"])
        and abs(row["rho_min_delta"]) <= 1.0e-3
        and abs(row["rho_max_delta"]) <= 1.0e-3
        and abs(row["lbm_max_v_delta"]) <= 1.0e-3
        and abs(row["mpm_min_J_delta"]) <= 1.0e-3
        and abs(row["projected_mass_delta"]) <= 1.0e-4
        and 0.25 <= row["link_area_area_scale_final"] <= 2.0
        and _finite_values(row, excluded=("candidate_id", "engineering_case", "link_area_case", "comparison_pass", "scope_note"))
    )
    return [row]


def summarize_engineering_vs_link_area_rows(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row["comparison_pass"])),
        "max_abs_rho_min_delta": max(abs(float(row["rho_min_delta"])) for row in rows) if rows else 0.0,
        "max_abs_rho_max_delta": max(abs(float(row["rho_max_delta"])) for row in rows) if rows else 0.0,
        "max_abs_lbm_max_v_delta": max(abs(float(row["lbm_max_v_delta"])) for row in rows) if rows else 0.0,
        "max_abs_mpm_min_J_delta": max(abs(float(row["mpm_min_J_delta"])) for row in rows) if rows else 0.0,
        "max_abs_projected_mass_delta": max(abs(float(row["projected_mass_delta"])) for row in rows) if rows else 0.0,
        "scope_note": SCOPE_NOTE,
    }


def assert_engineering_vs_link_area_summary(summary: dict) -> None:
    if int(summary["row_count"]) != 1 or int(summary["pass_count"]) != 1:
        raise RuntimeError(f"Step 31 engineering/link-area comparison must have one passing row: {summary}")
    if float(summary["max_abs_rho_min_delta"]) > 1.0e-3:
        raise RuntimeError(f"Step 31 rho_min delta exceeds tolerance: {summary}")
    if float(summary["max_abs_rho_max_delta"]) > 1.0e-3:
        raise RuntimeError(f"Step 31 rho_max delta exceeds tolerance: {summary}")
    if float(summary["max_abs_lbm_max_v_delta"]) > 1.0e-3:
        raise RuntimeError(f"Step 31 lbm_max_v delta exceeds tolerance: {summary}")
    if float(summary["max_abs_mpm_min_J_delta"]) > 1.0e-3:
        raise RuntimeError(f"Step 31 mpm_min_J delta exceeds tolerance: {summary}")
    if float(summary["max_abs_projected_mass_delta"]) > 1.0e-4:
        raise RuntimeError(f"Step 31 projected mass delta exceeds tolerance: {summary}")


def write_region_driver_summary(rows: list[dict], csv_path, json_path, summary=None) -> None:
    summary_payload = summarize_alignment_rows(rows) if summary is None else summary
    _write_csv(csv_path, rows, _fieldnames(rows))
    _write_json(json_path, {"summary": summary_payload, "rows": rows})


def _single_driver_row(rows: list[dict], mode: str, transfer: str) -> dict:
    matches = [row for row in rows if row["mode"] == mode and row["reaction_transfer_mode"] == transfer]
    if len(matches) != 1:
        raise RuntimeError(f"expected one Step 31 row for {mode}/{transfer}, found {len(matches)}")
    return matches[0]


def _region_mass(by_region: dict, region_id: str) -> float:
    if region_id not in by_region:
        return 0.0
    return float(by_region[region_id]["projected_mass"])


def _finite_values(row: dict, excluded=()) -> bool:
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _write_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[3] / path_obj
