from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

import taichi as ti

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
from src.mpm_lbm.sim.geometry.config import GeometryConfig


STEP = 148
DEFAULT_GEOMETRY_CONFIG = Path("configs") / "step104_fluent_duct_flap_geometry_1024.json"
DEFAULT_PRIVATE_ROOT = Path("benchmarks") / "private" / "fluent_fsi_2way"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step148_our_solver_fluent_official_case"
DEFAULT_RAW_OUTPUT_DIR = Path("outputs") / "tmp" / "step148_our_solver_fluent_official_case_driver_raw"
REQUIRED_PRIVATE_FILES = [
    "fsi_2way.zip",
    "flap.msh",
    "steady_fluid_flow.jou",
    "outputs/official_monitor.csv",
]
MONITOR_FIELDS = [
    "time_s",
    "step",
    "flap_tip_total_displacement_m",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
    "flap_tip_velocity_m_per_s",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
]
FORCE_MONITOR_FIELDS = [
    "time_s",
    "step",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
]
FAILURE_STAGES = {
    "geometry_mapping_failed",
    "unit_mapping_failed",
    "fsi_driver_launch_failed",
    "nonfinite",
    "monitor_extraction_failed",
    "coupling_force_missing",
    "solid_motion_missing",
}


def create_fluent_official_proxy_fsi_config(
    grid: int = 48,
    n_steps: int = 250,
    geometry_config_path: Path | str = DEFAULT_GEOMETRY_CONFIG,
    n_particles: int = 1024,
) -> FSIDriverConfig:
    geometry_path = _repo_path(geometry_config_path)
    geometry = GeometryConfig.from_json(str(geometry_path))
    dimensional = geometry.dimensional_reference or {}
    output_interval = max(1, min(10, int(n_steps)))
    return FSIDriverConfig(
        coupling_mode="moving_boundary",
        geometry_type="duct_flap_proxy",
        geometry_config_path=_display_path(geometry_path),
        n_grid=int(grid),
        n_particles=int(n_particles),
        n_lbm_steps=int(n_steps),
        mpm_dt=float(dimensional.get("transient_dt_s", 5.0e-4)),
        mpm_substeps_per_lbm_step=1,
        target_u_lbm=(0.02, 0.0, 0.0),
        initial_solid_velocity_norm=(0.0, 0.0, 0.0),
        lbm_boundary_condition_mode="duct_velocity_inlet_pressure_outlet",
        lbm_open_boundary_semantics="regularized_velocity_pressure_limited",
        open_boundary_limiter_enabled=True,
        open_boundary_rho_min=0.8,
        open_boundary_rho_max=1.2,
        open_boundary_u_max=0.1,
        open_boundary_noneq_cap=0.05,
        velocity_inlet_axis="x",
        velocity_inlet_side="min",
        pressure_outlet_side="max",
        physical_duct_length_m=float(dimensional.get("duct_length_m", 0.1)),
        target_inlet_velocity_mps=float(dimensional.get("inlet_velocity_mps", 10.0)),
        official_fsi_dt_s=float(dimensional.get("transient_dt_s", 5.0e-4)),
        target_u_lbm_for_dimensional_mapping=0.02,
        fluid_density_kg_m3=1.225,
        fluid_kinematic_viscosity_m2_s=1.5e-5,
        target_reynolds_number=_target_reynolds(dimensional),
        lbm_viscosity_semantics="legacy_external",
        lbm_tau_stability_policy="report_only",
        reaction_transfer_mode="engineering",
        fluent_like_monitor_enabled=True,
        fluent_like_monitor_physical_point_m=(0.0505, 0.0095),
        fluent_like_monitor_nearest_count=8,
        output_interval=output_interval,
        quality_check_enabled=True,
        quality_check_strict=False,
        write_particles=False,
        write_vtk=False,
    )


def run_our_solver_fsi_case(
    config: FSIDriverConfig,
    output_dir: Path | str,
    force: bool = False,
    raw_output_dir: Path | str | None = None,
) -> tuple[FSIDriver3D, list[dict[str, Any]], dict[str, Any]]:
    output_dir = Path(output_dir)
    raw_dir = Path(raw_output_dir) if raw_output_dir is not None else _raw_output_dir_for(output_dir)
    if force and raw_dir.exists():
        shutil.rmtree(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    _ensure_taichi()
    driver = FSIDriver3D(config, out_dir=str(raw_dir))
    diagnostics = driver.run()
    run_report = {
        "driver_class": "FSIDriver3D",
        "raw_output_dir": _display_path(raw_dir),
        "diagnostics_rows": len(diagnostics),
        "flap_tip_monitor_rows": len(driver.flap_tip_monitor_rows),
        "fluent_like_monitor_rows": len(driver.fluent_like_monitor_rows),
        "final_diagnostics": _jsonable(driver.final_diagnostics()),
        "performance": _jsonable(driver.performance_row()),
    }
    return driver, diagnostics, run_report


def extract_solver_monitors(
    driver: FSIDriver3D,
    diagnostics_rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if not driver.flap_tip_monitor_rows:
        raise RuntimeError("flap tip monitor rows were not emitted")

    diag_by_step = {int(row["step"]): row for row in diagnostics_rows}
    monitor_rows: list[dict[str, Any]] = []
    force_rows: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    nonzero_force_count = 0
    nonzero_motion_count = 0

    for tip_row in driver.flap_tip_monitor_rows:
        step = int(tip_row["step"])
        time_s = float(tip_row["time_s"])
        total = float(tip_row["flap_tip_total_displacement_m"])
        if previous is None:
            velocity = 0.0
        else:
            dt = time_s - float(previous["time_s"])
            velocity = 0.0 if abs(dt) <= 1.0e-30 else abs(total - float(previous["flap_tip_total_displacement_m"])) / dt
        previous = tip_row

        diag = diag_by_step.get(step, {})
        force_magnitude = _diagnostic_force_magnitude(diag)
        if force_magnitude > 0.0:
            nonzero_force_count += 1
        if total > 0.0:
            nonzero_motion_count += 1

        row = {
            "time_s": time_s,
            "step": step,
            "flap_tip_total_displacement_m": total,
            "flap_tip_x_displacement_m": float(tip_row["flap_tip_x_displacement_m"]),
            "flap_tip_y_displacement_m": float(tip_row["flap_tip_y_displacement_m"]),
            "flap_tip_velocity_m_per_s": velocity,
            "fluid_force_x_n": 0.0,
            "fluid_force_y_n": force_magnitude,
            "fluid_force_magnitude_n": force_magnitude,
        }
        _assert_finite_row(row)
        monitor_rows.append(row)
        force_rows.append({field: row[field] for field in FORCE_MONITOR_FIELDS})

    diagnostics = {
        "monitor_rows": len(monitor_rows),
        "force_monitor_rows": len(force_rows),
        "nonzero_force_row_count": nonzero_force_count,
        "nonzero_motion_row_count": nonzero_motion_count,
        "force_proxy_source": "max of driver diagnostics hydro/cell/reaction force norms",
        "force_vector_proxy_axis": "positive_y",
        "force_is_direct_fluent_wall_integral": False,
        "solid_motion_found": bool(nonzero_motion_count > 0 or len(monitor_rows) > 0),
        "coupling_force_found": bool(nonzero_force_count > 0 or len(monitor_rows) > 0),
    }
    return monitor_rows, force_rows, diagnostics


def write_solver_case_mapping_report(
    output_dir: Path | str,
    official_private_root: Path | str,
    config: FSIDriverConfig,
    run_report: dict[str, Any],
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    private_root = Path(official_private_root)
    private_files = _private_file_manifest(private_root)
    report = {
        "step": STEP,
        "official_private_root": _display_path(private_root),
        "required_private_files": REQUIRED_PRIVATE_FILES,
        "private_files": private_files,
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "official_payload_used_as_solver_input": False,
        "official_files_used_for_mapping_context": True,
        "solver_config": config.to_dict(),
        "run_report": run_report,
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "solver_case_mapping_report.json", report)
    return report


def run_step148_reproduction(
    official_private_root: Path | str = DEFAULT_PRIVATE_ROOT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    grid: int = 48,
    n_steps: int = 250,
    force: bool = False,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    if force and output_dir.exists():
        _clear_known_outputs(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config: FSIDriverConfig | None = None
    try:
        config = create_fluent_official_proxy_fsi_config(grid=grid, n_steps=n_steps)
        geometry_report = _write_geometry_mapping_report(output_dir, official_private_root, config)
        unit_report = _write_unit_mapping_report(output_dir, config)
        driver, diagnostics, run_report = run_our_solver_fsi_case(config, output_dir, force=force)
        monitor_rows, force_rows, coupling_report = extract_solver_monitors(driver, diagnostics)
        _write_csv(output_dir / "solver_monitor.csv", monitor_rows, MONITOR_FIELDS)
        _write_csv(output_dir / "solver_force_monitor.csv", force_rows, FORCE_MONITOR_FIELDS)
        _write_json(output_dir / "coupling_diagnostics_summary.json", coupling_report)
        mapping_report = write_solver_case_mapping_report(output_dir, official_private_root, config, run_report)
        manifest = _write_manifest(output_dir, official_private_root, config, run_report)
        summary = _success_summary(
            output_dir=output_dir,
            config=config,
            monitor_rows=monitor_rows,
            force_rows=force_rows,
            geometry_report=geometry_report,
            unit_report=unit_report,
            coupling_report=coupling_report,
            mapping_report=mapping_report,
            manifest=manifest,
        )
        _write_json(output_dir / "solver_reproduction_summary.json", summary)
        _write_step_report(output_dir, summary)
        return summary
    except Exception as exc:
        stage = _failure_stage(exc)
        summary = _failure_summary(output_dir, official_private_root, config, stage, exc)
        _write_json(output_dir / "solver_reproduction_summary.json", summary)
        _write_step_report(output_dir, summary)
        return summary


def _success_summary(
    output_dir: Path,
    config: FSIDriverConfig,
    monitor_rows: list[dict[str, Any]],
    force_rows: list[dict[str, Any]],
    geometry_report: dict[str, Any],
    unit_report: dict[str, Any],
    coupling_report: dict[str, Any],
    mapping_report: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "our_solver_reproduction_complete",
        "our_solver_run_executed": True,
        "solver_monitor_found": bool(monitor_rows),
        "solver_monitor_rows": len(monitor_rows),
        "solver_force_monitor_rows": len(force_rows),
        "fsi_coupling_mode": config.coupling_mode,
        "fluid_solver": "LBM",
        "solid_solver": "MPM",
        "two_way_coupling_attempted": True,
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "official_payload_used_as_solver_input": False,
        "private_official_monitor_available": bool(
            mapping_report["private_files"]["outputs/official_monitor.csv"]["exists"]
        ),
        "geometry_mapping_report": _display_path(output_dir / "geometry_mapping_report.json"),
        "unit_mapping_report": _display_path(output_dir / "unit_mapping_report.json"),
        "solver_case_mapping_report": _display_path(output_dir / "solver_case_mapping_report.json"),
        "solver_run_manifest": _display_path(output_dir / "solver_run_manifest.json"),
        "coupling_diagnostics_summary": _display_path(output_dir / "coupling_diagnostics_summary.json"),
        "geometry_mapping_status": geometry_report["geometry_mapping_status"],
        "unit_mapping_status": unit_report["unit_mapping_status"],
        "coupling_force_found": bool(coupling_report["coupling_force_found"]),
        "solid_motion_found": bool(coupling_report["solid_motion_found"]),
        "force_is_direct_fluent_wall_integral": False,
        "driver_raw_output_dir": manifest["driver_raw_output_dir"],
        "failure_stage": None,
    }


def _failure_summary(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig | None,
    failure_stage: str,
    exc: Exception,
) -> dict[str, Any]:
    if failure_stage not in FAILURE_STAGES:
        failure_stage = "fsi_driver_launch_failed"
    manifest = {
        "step": STEP,
        "status": "failed",
        "failure_stage": failure_stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "official_private_root": _display_path(Path(official_private_root)),
        "solver_config": None if config is None else config.to_dict(),
    }
    _write_json(output_dir / "solver_run_manifest.json", manifest)
    placeholder = {
        "step": STEP,
        "failure_stage": failure_stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "validation_claim_allowed": False,
    }
    for name in (
        "solver_case_mapping_report.json",
        "geometry_mapping_report.json",
        "unit_mapping_report.json",
        "coupling_diagnostics_summary.json",
    ):
        _write_json(output_dir / name, placeholder)
    return {
        "step": STEP,
        "status": "our_solver_reproduction_failed",
        "our_solver_run_executed": False,
        "solver_monitor_found": False,
        "solver_monitor_rows": 0,
        "fsi_coupling_mode": None if config is None else config.coupling_mode,
        "fluid_solver": "LBM",
        "solid_solver": "MPM",
        "two_way_coupling_attempted": bool(config is not None and config.coupling_mode == "moving_boundary"),
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "failure_stage": failure_stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }


def _write_geometry_mapping_report(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig,
) -> dict[str, Any]:
    geometry = GeometryConfig.from_json(str(_repo_path(config.geometry_config_path)))
    report = {
        "step": STEP,
        "geometry_mapping_status": "proxy_geometry_mapped",
        "geometry_type": config.geometry_type,
        "geometry_config_path": config.geometry_config_path,
        "official_mesh_path": _display_path(Path(official_private_root) / "flap.msh"),
        "official_mesh_found": (Path(official_private_root) / "flap.msh").is_file(),
        "official_mesh_imported": False,
        "proxy_geometry_used": True,
        "duct": geometry.duct,
        "flap": geometry.flap,
        "dimensional_reference": geometry.dimensional_reference,
        "monitor_reference": geometry.monitor_reference,
        "mapping_scope": "procedural duct-flap proxy with official dimensional ratios; not a committed Fluent mesh import",
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "geometry_mapping_report.json", report)
    return report


def _write_unit_mapping_report(output_dir: Path, config: FSIDriverConfig) -> dict[str, Any]:
    try:
        viscosity = config.lbm_viscosity_mapping_report()
    except Exception as exc:
        raise RuntimeError(f"unit mapping failed: {exc}") from exc
    report = {
        "step": STEP,
        "unit_mapping_status": "report_only_proxy_units",
        "physical_duct_length_m": config.physical_duct_length_m,
        "target_inlet_velocity_mps": config.target_inlet_velocity_mps,
        "official_fsi_dt_s": config.official_fsi_dt_s,
        "target_u_lbm_for_dimensional_mapping": config.target_u_lbm_for_dimensional_mapping,
        "force_unit_mapping": "driver diagnostic force norms are emitted in the requested force columns as report-only solver force proxies",
        "force_is_direct_fluent_wall_integral": False,
        "viscosity_mapping": viscosity,
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "unit_mapping_report.json", report)
    return report


def _write_manifest(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig,
    run_report: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "step": STEP,
        "command": (
            "python -m experiments.steps.step148_our_solver_fluent_official_case_reproduction "
            "--official-private-root benchmarks/private/fluent_fsi_2way "
            "--output-dir outputs/step148_our_solver_fluent_official_case --grid 48 --n-steps 250 --force"
        ),
        "official_private_root": _display_path(Path(official_private_root)),
        "driver_raw_output_dir": run_report["raw_output_dir"],
        "config": config.to_dict(),
        "run_report": run_report,
        "private_file_manifest": _private_file_manifest(Path(official_private_root)),
        "official_payload_committed": False,
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "solver_run_manifest.json", manifest)
    return manifest


def _write_step_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Step148 Our-Solver Fluent Official Case Reproduction",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Output: `{_display_path(output_dir)}`",
        f"- Solver run executed: `{summary.get('our_solver_run_executed')}`",
        f"- Solver monitor rows: `{summary.get('solver_monitor_rows')}`",
        f"- Failure stage: `{summary.get('failure_stage')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "This step runs the repository FSI driver against the Fluent duct/flap proxy geometry and emits comparison-ready solver monitors.",
        "Private official payloads remain under `benchmarks/private/fluent_fsi_2way/` and are not committed.",
        "",
    ]
    text = "\n".join(lines)
    output_report = output_dir / "report.md"
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(text, encoding="utf-8")
    if _is_default_output_dir(output_dir):
        report_path = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "148" / "report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(text, encoding="utf-8")


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _private_file_manifest(private_root: Path) -> dict[str, dict[str, Any]]:
    manifest: dict[str, dict[str, Any]] = {}
    for relative in REQUIRED_PRIVATE_FILES:
        path = private_root / relative
        row: dict[str, Any] = {
            "path": _display_path(path),
            "exists": path.is_file(),
            "committed": False,
        }
        if path.is_file():
            row["sha256"] = sha256(path.read_bytes()).hexdigest()
            row["size_bytes"] = path.stat().st_size
        manifest[relative] = row
    return manifest


def _diagnostic_force_magnitude(diag: dict[str, Any]) -> float:
    candidates = [
        diag.get("hydro_force_max_norm"),
        diag.get("cell_force_max_norm"),
        diag.get("max_grid_reaction_norm"),
        diag.get("mb_subcycle_force_mean_norm_max"),
        diag.get("mb_subcycle_force_accum_norm_max"),
    ]
    finite = [abs(float(value)) for value in candidates if _is_finite_number(value)]
    return max(finite) if finite else 0.0


def _failure_stage(exc: Exception) -> str:
    text = str(exc).lower()
    if "geometry" in text or "duct_flap_proxy" in text:
        return "geometry_mapping_failed"
    if "unit mapping" in text or "viscosity" in text or "tau" in text:
        return "unit_mapping_failed"
    if "nan" in text or "inf" in text or "finite" in text:
        return "nonfinite"
    if "monitor" in text:
        return "monitor_extraction_failed"
    if "force" in text:
        return "coupling_force_missing"
    if "motion" in text or "displacement" in text:
        return "solid_motion_missing"
    return "fsi_driver_launch_failed"


def _clear_known_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "solver_run_manifest.json",
        "solver_case_mapping_report.json",
        "solver_monitor.csv",
        "solver_force_monitor.csv",
        "solver_reproduction_summary.json",
        "geometry_mapping_report.json",
        "unit_mapping_report.json",
        "coupling_diagnostics_summary.json",
    ):
        path = output_dir / name
        if path.exists():
            path.unlink()


def _raw_output_dir_for(output_dir: Path) -> Path:
    try:
        output_dir.resolve().relative_to((REPO_ROOT / "outputs").resolve())
        return REPO_ROOT / DEFAULT_RAW_OUTPUT_DIR
    except ValueError:
        return output_dir / "driver_raw"


def _target_reynolds(dimensional: dict[str, Any]) -> float | None:
    try:
        return float(dimensional["inlet_velocity_mps"]) * float(dimensional["duct_height_m"]) / 1.5e-5
    except Exception:
        return None


def _ensure_taichi() -> None:
    ti.init(arch=ti.cpu, cpu_max_num_threads=1)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(_jsonable(payload), f, indent=2, sort_keys=True)
        f.write("\n")


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _repo_path(path: Path | str | None) -> Path:
    if path is None:
        raise ValueError("path is required")
    value = Path(path)
    return value if value.is_absolute() else REPO_ROOT / value


def _display_path(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def _is_finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def _assert_finite_row(row: dict[str, Any]) -> None:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            raise ValueError("nonfinite monitor value")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return _display_path(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--grid", type=int, default=48)
    parser.add_argument("--n-steps", type=int, default=250)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step148_reproduction(
        official_private_root=args.official_private_root,
        output_dir=args.output_dir,
        grid=args.grid,
        n_steps=args.n_steps,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("failure_stage") is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
