from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from .fluent_duct_flap_io import display_path, load_npz, resolve_repo_path, write_csv


VELOCITY_SCALE_MPS_PER_LBM = 500.0

CENTERLINE_FIELDS = [
    "x_index",
    "x_norm",
    "x_m",
    "y_index",
    "y_norm",
    "z_index",
    "z_norm",
    "rho",
    "ux_lbm",
    "uy_lbm",
    "uz_lbm",
    "speed_lbm",
    "ux_mps_proxy",
    "uy_mps_proxy",
    "uz_mps_proxy",
    "speed_mps_proxy",
    "solid",
    "fluid_mask",
]

X_PLANE_FLUX_FIELDS = [
    "x_index",
    "x_norm",
    "x_m",
    "fluid_cell_count_static_mask",
    "fluid_cell_count_dynamic_solver",
    "mass_flux_lbm",
    "mean_ux_lbm",
    "mean_speed_lbm",
    "max_speed_lbm",
    "mass_flux_mps_proxy_sum",
    "outlet_plane",
    "inlet_plane",
    "midplane",
]


def load_velocity_snapshot(snapshot_path: Path) -> dict[str, Any]:
    snapshot = load_npz(snapshot_path)
    required = {"velocity", "rho", "solid", "speed", "ux", "uy", "uz", "step", "time_s"}
    missing = sorted(required.difference(snapshot))
    if missing:
        raise KeyError(f"velocity snapshot missing keys: {missing}")
    return snapshot


def load_step154_masks(compiled_case: dict) -> dict[str, dict[str, np.ndarray]]:
    artifacts = compiled_case["mask_artifacts"]
    return {
        "geometry": load_npz(resolve_repo_path(artifacts["geometry_masks"])),
        "boundary": load_npz(resolve_repo_path(artifacts["boundary_masks"])),
        "fsi_interface": load_npz(resolve_repo_path(artifacts["fsi_interface_masks"])),
    }


def build_velocity_field_summary(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
) -> dict[str, Any]:
    velocity = np.asarray(snapshot["velocity"])
    rho = np.asarray(snapshot["rho"])
    speed = np.asarray(snapshot["speed"])
    solid = np.asarray(snapshot["solid"])
    fluid_mask = np.asarray(masks["geometry"]["fluid_mask"], dtype=bool)
    dynamic_fluid = solid == 0

    finite = bool(np.isfinite(velocity).all() and np.isfinite(rho).all() and np.isfinite(speed).all())
    return {
        "step": 156,
        "status": "final_snapshot_field_summary_written",
        "source_snapshot_step": int(np.asarray(snapshot["step"]).item()),
        "source_snapshot_time_s": float(np.asarray(snapshot["time_s"]).item()),
        "velocity_shape": list(velocity.shape),
        "rho_shape": list(rho.shape),
        "speed_min_lbm": float(np.nanmin(speed)),
        "speed_max_lbm": float(np.nanmax(speed)),
        "speed_max_mps_proxy": float(np.nanmax(speed) * VELOCITY_SCALE_MPS_PER_LBM),
        "ux_min_lbm": float(np.nanmin(snapshot["ux"])),
        "ux_max_lbm": float(np.nanmax(snapshot["ux"])),
        "uy_min_lbm": float(np.nanmin(snapshot["uy"])),
        "uy_max_lbm": float(np.nanmax(snapshot["uy"])),
        "uz_min_lbm": float(np.nanmin(snapshot["uz"])),
        "uz_max_lbm": float(np.nanmax(snapshot["uz"])),
        "rho_min": float(np.nanmin(rho)),
        "rho_max": float(np.nanmax(rho)),
        "finite_field_values": finite,
        "static_fluid_cell_count": int(fluid_mask.sum()),
        "dynamic_fluid_cell_count": int(dynamic_fluid.sum()),
        "monitor_index": list(compiled_case["monitor_spec"]["monitor_index"]),
        "velocity_scale_mps_per_lbm": VELOCITY_SCALE_MPS_PER_LBM,
        "velocity_scale_note": "proxy m/s from Step155 target_u_lbm mapping; not Fluent validation",
        "validation_claim_allowed": False,
    }


def write_velocity_magnitude_plot(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
    title: str | None = None,
) -> dict[str, Any]:
    field = np.asarray(snapshot["speed"])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    return _write_field_plot(
        field,
        snapshot,
        masks,
        compiled_case,
        output_path,
        slice_index,
        title=title
        or f"Step155 step 50, t = {float(np.asarray(snapshot['time_s']).item()):.3f} s; proxy solver result",
        colorbar_label="Velocity magnitude [m/s proxy]",
        cmap="viridis",
        signed=False,
    )


def write_velocity_component_plot(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    component: str,
    slice_index: int,
    title: str | None = None,
) -> dict[str, Any]:
    if component not in {"ux", "uy", "uz"}:
        raise ValueError(f"unsupported velocity component: {component}")
    field = np.asarray(snapshot[component])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    return _write_field_plot(
        field,
        snapshot,
        masks,
        compiled_case,
        output_path,
        slice_index,
        title=title or f"{component} diagnostic; not Fluent validation",
        colorbar_label=f"{component} [m/s proxy]",
        cmap="coolwarm",
        signed=True,
    )


def write_streamline_or_quiver_plot(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
) -> dict[str, Any]:
    _ensure_parent(output_path)
    ux = np.asarray(snapshot["ux"])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    uy = np.asarray(snapshot["uy"])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    speed = np.asarray(snapshot["speed"])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    solid = _solid_slice(snapshot, masks, slice_index)
    ux = np.where(solid, np.nan, ux)
    uy = np.where(solid, np.nan, uy)

    stride = max(1, ux.shape[0] // 18)
    x = np.arange(ux.shape[0])
    y = np.arange(ux.shape[1])
    xx, yy = np.meshgrid(x, y, indexing="ij")

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=160)
    image = ax.imshow(
        np.ma.array(speed, mask=solid).T,
        origin="lower",
        aspect="auto",
        cmap="viridis",
    )
    ax.quiver(
        xx[::stride, ::stride],
        yy[::stride, ::stride],
        ux[::stride, ::stride],
        uy[::stride, ::stride],
        color="white",
        scale=250,
        width=0.003,
    )
    _add_geometry_overlay(ax, snapshot, masks, compiled_case, slice_index)
    ax.set_title("Step155 step 50 ux/uy quiver; not Fluent validation")
    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    fig.colorbar(image, ax=ax, label="Velocity magnitude [m/s proxy]")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return _plot_report(output_path, "streamline_or_quiver_plot_written", slice_index)


def write_geometry_overlay_plot(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
) -> dict[str, Any]:
    _ensure_parent(output_path)
    geometry = masks["geometry"]
    boundary = masks["boundary"]
    interface = masks["fsi_interface"]

    code = np.zeros_like(geometry["solid_mask"][:, :, slice_index], dtype=np.int16)
    code[geometry["fluid_mask"][:, :, slice_index]] = 1
    code[geometry["solid_mask"][:, :, slice_index]] = 2
    code[geometry["flap_solid_mask"][:, :, slice_index]] = 3
    code[interface["fluid_interface_mask"][:, :, slice_index]] = 4
    code[boundary["velocity_inlet_mask"][:, :, slice_index]] = 5
    code[boundary["pressure_outlet_mask"][:, :, slice_index]] = 6
    code[geometry["monitor_cell_mask"][:, :, slice_index]] = 7

    cmap = ListedColormap(
        [
            "#f4f4f4",
            "#4c78a8",
            "#d9d9d9",
            "#f58518",
            "#54a24b",
            "#e45756",
            "#72b7b2",
            "#b279a2",
        ]
    )
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=160)
    image = ax.imshow(code.T, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=7)
    _add_monitor(ax, compiled_case)
    ax.set_title("Step156 geometry and mask overlay")
    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    colorbar = fig.colorbar(image, ax=ax, ticks=list(range(8)))
    colorbar.ax.set_yticklabels(
        ["outside", "fluid", "solid", "flap", "interface", "inlet", "outlet", "monitor"]
    )
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return _plot_report(output_path, "geometry_overlay_written", slice_index)


def write_official_style_velocity_cloud_plot(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
    title: str | None = None,
) -> dict[str, Any]:
    field = np.asarray(snapshot["speed"])[:, :, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
    return _write_field_plot(
        field,
        snapshot,
        masks,
        compiled_case,
        output_path,
        slice_index,
        title=title or "Step155 proxy solver result; not Fluent validation",
        colorbar_label="Velocity magnitude [m/s proxy]",
        cmap="turbo",
        signed=False,
        figsize=(10.0, 3.8),
    )


def write_centerline_velocity_profile(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
) -> dict[str, Any]:
    rho = np.asarray(snapshot["rho"])
    ux = np.asarray(snapshot["ux"])
    uy = np.asarray(snapshot["uy"])
    uz = np.asarray(snapshot["uz"])
    speed = np.asarray(snapshot["speed"])
    solid = np.asarray(snapshot["solid"])
    fluid_mask = np.asarray(masks["geometry"]["fluid_mask"], dtype=bool)
    nx, ny, nz = rho.shape
    y_index = _centerline_y_index(compiled_case, ny)
    rows = []
    for x_index in range(nx):
        x_norm = _cell_norm(x_index, nx)
        y_norm = _cell_norm(y_index, ny)
        z_norm = _cell_norm(slice_index, nz)
        row = {
            "x_index": x_index,
            "x_norm": x_norm,
            "x_m": _x_m(compiled_case, x_norm),
            "y_index": y_index,
            "y_norm": y_norm,
            "z_index": slice_index,
            "z_norm": z_norm,
            "rho": float(rho[x_index, y_index, slice_index]),
            "ux_lbm": float(ux[x_index, y_index, slice_index]),
            "uy_lbm": float(uy[x_index, y_index, slice_index]),
            "uz_lbm": float(uz[x_index, y_index, slice_index]),
            "speed_lbm": float(speed[x_index, y_index, slice_index]),
            "ux_mps_proxy": float(ux[x_index, y_index, slice_index] * VELOCITY_SCALE_MPS_PER_LBM),
            "uy_mps_proxy": float(uy[x_index, y_index, slice_index] * VELOCITY_SCALE_MPS_PER_LBM),
            "uz_mps_proxy": float(uz[x_index, y_index, slice_index] * VELOCITY_SCALE_MPS_PER_LBM),
            "speed_mps_proxy": float(
                speed[x_index, y_index, slice_index] * VELOCITY_SCALE_MPS_PER_LBM
            ),
            "solid": int(solid[x_index, y_index, slice_index]),
            "fluid_mask": bool(fluid_mask[x_index, y_index, slice_index]),
        }
        rows.append(row)

    write_csv(output_path, rows, CENTERLINE_FIELDS)
    return {
        "status": "centerline_velocity_profile_written",
        "path": display_path(output_path),
        "row_count": len(rows),
        "y_index": y_index,
        "z_index": slice_index,
        "validation_claim_allowed": False,
    }


def write_x_plane_flux_profile(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
) -> dict[str, Any]:
    rho = np.asarray(snapshot["rho"])
    ux = np.asarray(snapshot["ux"])
    speed = np.asarray(snapshot["speed"])
    solid = np.asarray(snapshot["solid"])
    static_fluid = np.asarray(masks["geometry"]["fluid_mask"], dtype=bool)
    inlet_mask = np.asarray(masks["boundary"]["velocity_inlet_mask"], dtype=bool)
    outlet_mask = np.asarray(masks["boundary"]["pressure_outlet_mask"], dtype=bool)
    dynamic_fluid = solid == 0
    nx = rho.shape[0]
    midplane = nx // 2
    rows = []
    for x_index in range(nx):
        plane = dynamic_fluid[x_index]
        fluid_count = int(plane.sum())
        mass_flux = float(np.sum(rho[x_index][plane] * ux[x_index][plane])) if fluid_count else 0.0
        mean_ux = float(np.mean(ux[x_index][plane])) if fluid_count else 0.0
        mean_speed = float(np.mean(speed[x_index][plane])) if fluid_count else 0.0
        max_speed = float(np.max(speed[x_index][plane])) if fluid_count else 0.0
        x_norm = _cell_norm(x_index, nx)
        rows.append(
            {
                "x_index": x_index,
                "x_norm": x_norm,
                "x_m": _x_m(compiled_case, x_norm),
                "fluid_cell_count_static_mask": int(static_fluid[x_index].sum()),
                "fluid_cell_count_dynamic_solver": fluid_count,
                "mass_flux_lbm": mass_flux,
                "mean_ux_lbm": mean_ux,
                "mean_speed_lbm": mean_speed,
                "max_speed_lbm": max_speed,
                "mass_flux_mps_proxy_sum": mass_flux * VELOCITY_SCALE_MPS_PER_LBM,
                "outlet_plane": bool(outlet_mask[x_index].any()),
                "inlet_plane": bool(inlet_mask[x_index].any()),
                "midplane": x_index == midplane,
            }
        )

    write_csv(output_path, rows, X_PLANE_FLUX_FIELDS)
    return {
        "status": "x_plane_flux_profile_written",
        "path": display_path(output_path),
        "row_count": len(rows),
        "validation_claim_allowed": False,
    }


def _write_field_plot(
    field: np.ndarray,
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    output_path: Path,
    slice_index: int,
    title: str,
    colorbar_label: str,
    cmap: str,
    signed: bool,
    figsize: tuple[float, float] = (8.5, 4.8),
) -> dict[str, Any]:
    _ensure_parent(output_path)
    solid = _solid_slice(snapshot, masks, slice_index)
    masked = np.ma.array(field, mask=solid)
    fig, ax = plt.subplots(figsize=figsize, dpi=160)
    kwargs = {"origin": "lower", "aspect": "auto", "cmap": cmap}
    if signed:
        vmax = float(np.nanmax(np.abs(field))) if np.isfinite(field).any() else 1.0
        kwargs.update({"vmin": -vmax, "vmax": vmax})
    image = ax.imshow(masked.T, **kwargs)
    _add_geometry_overlay(ax, snapshot, masks, compiled_case, slice_index)
    ax.set_title(title)
    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    fig.colorbar(image, ax=ax, label=colorbar_label)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return _plot_report(output_path, "plot_written", slice_index)


def _add_geometry_overlay(
    ax: Any,
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    compiled_case: dict,
    slice_index: int,
) -> None:
    solid = _solid_slice(snapshot, masks, slice_index)
    flap = np.asarray(masks["geometry"]["flap_solid_mask"], dtype=bool)[:, :, slice_index]
    inlet = np.asarray(masks["boundary"]["velocity_inlet_mask"], dtype=bool)[:, :, slice_index]
    outlet = np.asarray(masks["boundary"]["pressure_outlet_mask"], dtype=bool)[:, :, slice_index]

    ax.contour(solid.T.astype(float), levels=[0.5], colors="black", linewidths=0.5)
    if flap.any():
        ax.contour(flap.T.astype(float), levels=[0.5], colors="orange", linewidths=1.0)
    _scatter_mask_center(ax, inlet, "inlet", "#e45756")
    _scatter_mask_center(ax, outlet, "outlet", "#72b7b2")
    _add_monitor(ax, compiled_case)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.75)


def _add_monitor(ax: Any, compiled_case: dict) -> None:
    monitor = compiled_case["monitor_spec"]["monitor_index"]
    ax.scatter([monitor[0]], [monitor[1]], marker="x", color="white", s=55, label="monitor")
    ax.scatter([monitor[0]], [monitor[1]], marker="x", color="black", s=25)


def _scatter_mask_center(ax: Any, mask: np.ndarray, label: str, color: str) -> None:
    positions = np.argwhere(mask)
    if positions.size == 0:
        return
    center = positions.mean(axis=0)
    ax.scatter([center[0]], [center[1]], color=color, s=24, label=label)


def _solid_slice(
    snapshot: dict,
    masks: dict[str, dict[str, np.ndarray]],
    slice_index: int,
) -> np.ndarray:
    snapshot_solid = np.asarray(snapshot["solid"])[:, :, slice_index] != 0
    mask_solid = np.asarray(masks["geometry"]["solid_mask"], dtype=bool)[:, :, slice_index]
    return np.logical_or(snapshot_solid, mask_solid)


def _centerline_y_index(compiled_case: dict, ny: int) -> int:
    duct_y_min, duct_y_max = compiled_case["solver_geometry_mapping"]["duct_normalized"]["y"]
    y_center = 0.5 * (float(duct_y_min) + float(duct_y_max))
    centers = (np.arange(ny) + 0.5) / ny
    return int(np.argmin(np.abs(centers - y_center)))


def _cell_norm(index: int, count: int) -> float:
    return float((index + 0.5) / count)


def _x_m(compiled_case: dict, x_norm: float) -> float:
    return float(compiled_case["official_tutorial_setup"]["duct_length_m"]) * x_norm


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _plot_report(output_path: Path, status: str, slice_index: int) -> dict[str, Any]:
    return {
        "status": status,
        "path": display_path(output_path),
        "slice_axis": "z",
        "slice_index": int(slice_index),
        "size_bytes": output_path.stat().st_size,
        "validation_claim_allowed": False,
    }
