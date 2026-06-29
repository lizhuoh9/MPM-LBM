from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from src.mpm_lbm.postprocessing.fluent_duct_flap_acceptance import (
    build_solver_acceptance_report,
    load_step155_summary,
    summarize_mass_flux,
    summarize_stability,
)
from src.mpm_lbm.postprocessing.fluent_duct_flap_io import (
    display_path,
    read_json,
    require_file,
    resolve_repo_path,
    write_json,
)
from src.mpm_lbm.postprocessing.fluent_duct_flap_monitor_plots import (
    summarize_monitor_rows,
    write_force_monitor_plot,
    write_monitor_displacement_plot,
)
from src.mpm_lbm.postprocessing.fluent_duct_flap_official_comparison import (
    build_official_comparison_report,
)
from src.mpm_lbm.postprocessing.fluent_duct_flap_velocity_render import (
    build_velocity_field_summary,
    load_step154_masks,
    load_velocity_snapshot,
    write_centerline_velocity_profile,
    write_geometry_overlay_plot,
    write_official_style_velocity_cloud_plot,
    write_streamline_or_quiver_plot,
    write_velocity_component_plot,
    write_velocity_magnitude_plot,
    write_x_plane_flux_profile,
)


STEP = 156
DEFAULT_OUTPUT_DIR = Path("outputs") / "step156_official_tutorial_postprocess_and_acceptance"


def run_step156_postprocess(
    case_path: Path | str,
    solver_root: Path | str,
    official_monitor_path: Path | str,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
    snapshot_step: int = 50,
    slice_z_index: int | None = None,
    use_monitor_z: bool = True,
    tail_fraction: float = 0.2,
    dpi: int = 160,
    no_preview_open: bool = True,
) -> dict[str, Any]:
    del dpi, no_preview_open
    case_path = require_file(case_path, "compiled case")
    solver_root = resolve_repo_path(solver_root)
    output_dir = resolve_repo_path(output_dir)
    if output_dir.exists():
        if not force:
            raise FileExistsError(f"output directory exists; pass force: {display_path(output_dir)}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    compiled_case = read_json(case_path)
    postprocess_spec_path = require_file(
        compiled_case["postprocess_spec_path"],
        "Step154 postprocess spec",
    )
    postprocess_spec = read_json(postprocess_spec_path)
    masks = load_step154_masks(compiled_case)
    step155_summary = load_step155_summary(solver_root)
    _validate_step155_summary(step155_summary)

    snapshot_path = require_file(
        solver_root / "velocity_snapshots" / f"velocity_snapshot_step{snapshot_step:03d}.npz",
        "Step155 final velocity snapshot",
    )
    snapshot = load_velocity_snapshot(snapshot_path)
    slice_index, slice_policy = _select_slice_index(compiled_case, snapshot, slice_z_index, use_monitor_z)

    field_summary = build_velocity_field_summary(snapshot, masks, compiled_case)
    field_summary.update(
        {
            "slice_axis": "z",
            "slice_index": slice_index,
            "slice_policy": slice_policy,
            "snapshot_step": int(snapshot_step),
            "snapshot_time_s": float(snapshot["time_s"].item()),
            "snapshot_path": display_path(snapshot_path),
        }
    )
    write_json(output_dir / "final_snapshot_field_summary.json", field_summary)

    magnitude = write_velocity_magnitude_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "velocity_magnitude_step050.png",
        slice_index,
    )
    velocity_ux = write_velocity_component_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "velocity_ux_step050.png",
        "ux",
        slice_index,
    )
    velocity_uy = write_velocity_component_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "velocity_uy_step050.png",
        "uy",
        slice_index,
    )
    quiver = write_streamline_or_quiver_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "streamline_or_quiver_step050.png",
        slice_index,
    )
    geometry = write_geometry_overlay_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "geometry_overlay_step050.png",
        slice_index,
    )
    velocity_cloud = write_official_style_velocity_cloud_plot(
        snapshot,
        masks,
        compiled_case,
        output_dir / "official_style_velocity_cloud_step050.png",
        slice_index,
    )
    centerline = write_centerline_velocity_profile(
        snapshot,
        masks,
        compiled_case,
        output_dir / "centerline_velocity_profile.csv",
        slice_index,
    )
    x_flux = write_x_plane_flux_profile(
        snapshot,
        masks,
        compiled_case,
        output_dir / "x_plane_flux_profile.csv",
    )
    velocity_render_report = {
        "step": STEP,
        "status": "velocity_render_complete",
        "slice_axis": "z",
        "slice_index": slice_index,
        "slice_policy": slice_policy,
        "snapshot_step": int(snapshot_step),
        "snapshot_time_s": float(snapshot["time_s"].item()),
        "velocity_magnitude_written": True,
        "velocity_ux_written": True,
        "velocity_uy_written": True,
        "streamline_or_quiver_written": True,
        "geometry_overlay_written": True,
        "official_style_velocity_cloud_written": True,
        "centerline_profile_written": True,
        "x_plane_flux_profile_written": True,
        "plot_reports": {
            "velocity_magnitude": magnitude,
            "velocity_ux": velocity_ux,
            "velocity_uy": velocity_uy,
            "streamline_or_quiver": quiver,
            "geometry_overlay": geometry,
            "official_style_velocity_cloud": velocity_cloud,
        },
        "profile_reports": {
            "centerline": centerline,
            "x_plane_flux": x_flux,
        },
        "velocity_scale_mps_per_lbm": 500.0,
        "velocity_scale_note": "proxy m/s from Step155 target_u_lbm mapping; not Fluent validation",
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "velocity_render_report.json", velocity_render_report)

    solver_monitor = require_file(solver_root / "solver_monitor.csv", "Step155 solver monitor")
    solver_force = require_file(solver_root / "solver_force_monitor.csv", "Step155 solver force monitor")
    displacement_plot = write_monitor_displacement_plot(
        solver_monitor,
        output_dir / "monitor_displacement_plot.png",
    )
    force_plot = write_force_monitor_plot(
        solver_force,
        output_dir / "force_monitor_plot.png",
    )
    monitor_report = summarize_monitor_rows(solver_monitor, solver_force)
    monitor_report.update(
        {
            "monitor_displacement_plot": displacement_plot,
            "force_monitor_plot": force_plot,
        }
    )
    write_json(output_dir / "monitor_plot_report.json", monitor_report)

    mass_flux_summary = summarize_mass_flux(solver_root / "mass_flux_timeseries.csv", tail_fraction)
    stability_summary = summarize_stability(solver_root / "stability_timeseries.csv")
    acceptance = build_solver_acceptance_report(
        step155_summary,
        mass_flux_summary,
        stability_summary,
        output_dir / "solver_acceptance_report.json",
    )
    official_comparison = build_official_comparison_report(
        Path(official_monitor_path),
        solver_monitor,
        output_dir / "official_comparison_report.json",
    )
    summary = _build_postprocess_summary(
        compiled_case,
        postprocess_spec,
        step155_summary,
        field_summary,
        velocity_render_report,
        monitor_report,
        acceptance,
        official_comparison,
        case_path,
        solver_root,
        postprocess_spec_path,
    )
    write_json(output_dir / "postprocess_summary.json", summary)
    report_text = _build_report_text(summary, acceptance)
    (output_dir / "report.md").write_text(report_text, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step156_postprocess(
        case_path=args.case,
        solver_root=args.solver_root,
        official_monitor_path=args.official_monitor,
        output_dir=args.output_dir,
        force=args.force,
        snapshot_step=args.snapshot_step,
        slice_z_index=args.slice_z_index,
        use_monitor_z=args.use_monitor_z,
        tail_fraction=args.tail_fraction,
        dpi=args.dpi,
        no_preview_open=args.no_preview_open,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step156 official tutorial postprocess")
    parser.add_argument("--case", required=True)
    parser.add_argument("--solver-root", required=True)
    parser.add_argument("--official-monitor", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--snapshot-step", type=int, default=50)
    parser.add_argument("--slice-z-index", type=int, default=None)
    parser.add_argument("--use-monitor-z", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--tail-fraction", type=float, default=0.2)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--no-preview-open", action="store_true")
    return parser.parse_args(argv)


def _validate_step155_summary(summary: dict[str, Any]) -> None:
    required = {
        "status": "official_tutorial_solver_v1_run_complete",
        "solver_v1_run_executed": True,
        "compiled_case_consumed": True,
        "n_steps_completed": 50,
        "time_end_s": 0.025,
        "validation_claim_allowed": False,
    }
    for key, expected in required.items():
        actual = summary.get(key)
        if actual != expected:
            raise ValueError(f"Step155 summary mismatch for {key}: expected {expected!r}, got {actual!r}")


def _select_slice_index(
    compiled_case: dict[str, Any],
    snapshot: dict[str, Any],
    explicit_slice: int | None,
    use_monitor_z: bool,
) -> tuple[int, str]:
    nz = int(snapshot["rho"].shape[2])
    if explicit_slice is not None:
        if not 0 <= explicit_slice < nz:
            raise ValueError(f"slice index out of range: {explicit_slice}")
        return explicit_slice, "explicit_slice_z_index"
    if use_monitor_z:
        z_index = int(compiled_case["monitor_spec"]["monitor_index"][2])
        if not 0 <= z_index < nz:
            raise ValueError(f"monitor z index out of range: {z_index}")
        return z_index, "monitor_z_index"
    return nz // 2, "domain_midplane_z_index"


def _build_postprocess_summary(
    compiled_case: dict[str, Any],
    postprocess_spec: dict[str, Any],
    step155_summary: dict[str, Any],
    field_summary: dict[str, Any],
    velocity_report: dict[str, Any],
    monitor_report: dict[str, Any],
    acceptance: dict[str, Any],
    official_comparison: dict[str, Any],
    case_path: Path,
    solver_root: Path,
    postprocess_spec_path: Path,
) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "official_tutorial_postprocess_complete",
        "preprocess_complete": compiled_case.get("status") == "compiled_case_ready_for_step155",
        "solver_complete": step155_summary.get("status") == "official_tutorial_solver_v1_run_complete",
        "postprocess_complete": True,
        "compiled_case_consumed": True,
        "step155_solver_root_consumed": True,
        "final_snapshot_loaded": True,
        "compiled_case_path": display_path(case_path),
        "postprocess_spec_path": display_path(postprocess_spec_path),
        "solver_root": display_path(solver_root),
        "postprocess_spec_status": postprocess_spec.get("status"),
        "snapshot_step": field_summary["snapshot_step"],
        "snapshot_time_s": field_summary["snapshot_time_s"],
        "slice_axis": "z",
        "slice_index": velocity_report["slice_index"],
        "slice_policy": velocity_report["slice_policy"],
        "velocity_cloud_written": True,
        "velocity_magnitude_written": True,
        "velocity_ux_written": True,
        "velocity_uy_written": True,
        "streamline_or_quiver_written": True,
        "geometry_overlay_written": True,
        "monitor_plots_written": True,
        "centerline_profile_written": True,
        "x_plane_flux_profile_written": True,
        "solver_acceptance_report_written": acceptance["status"]
        == "solver_acceptance_report_written",
        "official_comparison_report_written": True,
        "postprocess_acceptance_pass": acceptance["postprocess_acceptance_pass"],
        "solver_numerical_sanity_pass": acceptance["solver_numerical_sanity_pass"],
        "flow_development_gate_reported": acceptance["flow_development_gate_reported"],
        "flow_development_gate_pass": acceptance["flow_development_gate_pass"],
        "flow_development_gate_policy": acceptance["flow_development_gate_policy"],
        "inlet_flux_tail_mean": acceptance["inlet_flux_tail_mean"],
        "outlet_flux_tail_mean": acceptance["outlet_flux_tail_mean"],
        "flux_imbalance_rel_tail_mean": acceptance["flux_imbalance_rel_tail_mean"],
        "outlet_to_inlet_flux_ratio_tail_mean": acceptance[
            "outlet_to_inlet_flux_ratio_tail_mean"
        ],
        "official_monitor_loaded": official_comparison["official_monitor_loaded"],
        "official_error_metrics_available": official_comparison[
            "official_error_metrics_available"
        ],
        "solver_monitor_rows": monitor_report["solver_monitor_rows"],
        "solver_force_monitor_rows": monitor_report["solver_force_monitor_rows"],
        "solver_pipeline_complete": True,
        "official_validation_requires_monitor": True,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _build_report_text(summary: dict[str, Any], acceptance: dict[str, Any]) -> str:
    return (
        "# Step156 Official Tutorial Postprocess And Solver Acceptance\n\n"
        "Step156 consumed the Step154 compiled case and Step155 solver outputs and\n"
        "generated official-style postprocessing artifacts: velocity magnitude, ux, uy,\n"
        "stream/quiver, geometry overlay, centerline profile, x-plane flux profile,\n"
        "monitor plots, solver acceptance report, and official comparison report.\n\n"
        "Step156 did not run the solver. Step156 did not run Fluent. Step156 did not\n"
        "load or fabricate official monitor data when the private monitor was absent.\n"
        "Step156 did not run Step150 and does not make a validation claim.\n\n"
        "The current Step155 run passes numerical sanity gates, but flow-development\n"
        "acceptance is report-only and may fail because outlet flux is still near zero\n"
        "relative to inlet flux over the 0.025 s tutorial window.\n\n"
        "A later step must address solver physics / flow-development gaps before any\n"
        "Figure 29.3 parity or Fluent validation claim can be made.\n\n"
        "## Current Acceptance\n\n"
        f"- postprocess_complete: {summary['postprocess_complete']}\n"
        f"- solver_numerical_sanity_pass: {summary['solver_numerical_sanity_pass']}\n"
        f"- flow_development_gate_pass: {summary['flow_development_gate_pass']}\n"
        f"- inlet_flux_tail_mean: {acceptance['inlet_flux_tail_mean']}\n"
        f"- outlet_flux_tail_mean: {acceptance['outlet_flux_tail_mean']}\n"
        f"- flux_imbalance_rel_tail_mean: {acceptance['flux_imbalance_rel_tail_mean']}\n"
        f"- validation_claim_allowed: {summary['validation_claim_allowed']}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
