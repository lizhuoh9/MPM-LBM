from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any

import numpy as np


EXPECTED_OUTPUTS = {
    "velocity_magnitude_plot": "velocity_magnitude_step050.png",
    "velocity_ux_plot": "velocity_ux_step050.png",
    "velocity_uy_plot": "velocity_uy_step050.png",
    "streamline_or_quiver_plot": "streamline_or_quiver_step050.png",
    "geometry_overlay_plot": "geometry_overlay_step050.png",
    "centerline_velocity_profile": "centerline_velocity_profile.csv",
    "x_plane_flux_profile": "x_plane_flux_profile.csv",
    "monitor_displacement_plot": "monitor_displacement_plot.png",
    "force_monitor_plot": "force_monitor_plot.png",
    "postprocess_summary": "postprocess_summary.json",
    "solver_acceptance_report": "solver_acceptance_report.json",
    "official_comparison_report": "official_comparison_report.json",
}


def build_postprocess_spec(compiled_case: dict, output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    spec = {
        "step": 154,
        "status": "postprocess_spec_ready",
        "case_name": compiled_case["case_name"],
        "compiled_case_path": _display_path(output_dir / "compiled_case.json"),
        "expected_outputs": dict(EXPECTED_OUTPUTS),
        "geometry_preview_path": _display_path(output_dir / "geometry_preview.png"),
        "step156_required_before_velocity_plots": True,
        "official_monitor_required_before_comparison_report": True,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
    }
    _write_json(output_dir / "postprocess_spec.json", spec)
    return spec


def write_geometry_preview(compiled_case: dict, masks: dict, output_path: Path) -> dict:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = _write_matplotlib_preview(compiled_case, masks, output_path)
    except ModuleNotFoundError:
        report = _write_fallback_preview(compiled_case, masks, output_path)
    report.update(
        {
            "step": 154,
            "status": "geometry_preview_written",
            "geometry_preview_path": _display_path(output_path),
            "validation_claim_allowed": False,
        }
    )
    return report


def _write_matplotlib_preview(compiled_case: dict, masks: dict, output_path: Path) -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    geometry = masks["geometry"]
    boundary = masks["boundary"]
    k = int(compiled_case["monitor_spec"]["monitor_index"][2])
    fluid = geometry["fluid_mask"][:, :, k]
    flap = geometry["flap_solid_mask"][:, :, k]
    inlet = boundary["velocity_inlet_mask"][:, :, k]
    outlet = boundary["pressure_outlet_mask"][:, :, k]
    monitor = compiled_case["monitor_spec"]["monitor_point_normalized"]

    image = _preview_rgb_array(fluid, flap, inlet, outlet)
    fig, ax = plt.subplots(figsize=(8, 4), dpi=120)
    ax.imshow(np.swapaxes(image, 0, 1), origin="lower", extent=[0, 1, 0, 1])
    ax.scatter([monitor[0]], [monitor[1]], c="black", s=20, marker="x")
    ax.set_title("Step154 official duct/flap proxy geometry preview")
    ax.set_xlabel("x normalized")
    ax.set_ylabel("y normalized")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return {"preview_renderer": "matplotlib_agg"}


def _write_fallback_preview(compiled_case: dict, masks: dict, output_path: Path) -> dict:
    geometry = masks["geometry"]
    boundary = masks["boundary"]
    k = int(compiled_case["monitor_spec"]["monitor_index"][2])
    fluid = geometry["fluid_mask"][:, :, k]
    flap = geometry["flap_solid_mask"][:, :, k]
    inlet = boundary["velocity_inlet_mask"][:, :, k]
    outlet = boundary["pressure_outlet_mask"][:, :, k]
    image = _preview_rgb_array(fluid, flap, inlet, outlet)
    monitor_i, monitor_j, _ = [int(v) for v in compiled_case["monitor_spec"]["monitor_index"]]
    if 0 <= monitor_i < image.shape[0] and 0 <= monitor_j < image.shape[1]:
        image[monitor_i, monitor_j] = [0, 0, 0]
    scale = 8
    image = np.repeat(np.repeat(np.swapaxes(image, 0, 1), scale, axis=0), scale, axis=1)
    _write_png_rgb(output_path, image)
    return {"preview_renderer": "standard_library_png_fallback", "matplotlib_available": False}


def _preview_rgb_array(
    fluid: np.ndarray,
    flap: np.ndarray,
    inlet: np.ndarray,
    outlet: np.ndarray,
) -> np.ndarray:
    image = np.full((fluid.shape[0], fluid.shape[1], 3), [235, 235, 235], dtype=np.uint8)
    image[fluid] = [64, 164, 223]
    image[flap] = [70, 70, 70]
    image[inlet] = [46, 204, 113]
    image[outlet] = [231, 76, 60]
    return image


def _write_png_rgb(path: Path, image: np.ndarray) -> None:
    height, width, channels = image.shape
    if channels != 3:
        raise ValueError("fallback PNG writer expects RGB image")
    raw_rows = []
    for row in image:
        raw_rows.append(b"\x00" + row.tobytes())
    raw = b"".join(raw_rows)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += _png_chunk(b"IDAT", zlib.compress(raw))
    payload += _png_chunk(b"IEND", b"")
    path.write_bytes(payload)


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display_path(path: Path | str) -> str:
    try:
        return str(Path(path).relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
