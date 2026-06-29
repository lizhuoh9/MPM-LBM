"""Step154 official solver pre/post pipeline.

This step compiles a canonical case and pre/post artifacts from Step153 setup
parity outputs. It intentionally does not run Fluent, Step150, selected96, or
the FSI solver.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mpm_lbm.cases.fluent_duct_flap.postprocess import (  # noqa: E402
    build_postprocess_spec,
    write_geometry_preview,
)
from src.mpm_lbm.cases.fluent_duct_flap.preprocess import (  # noqa: E402
    build_boundary_masks,
    build_fsi_interface_masks,
    build_geometry_masks,
    compile_official_duct_flap_case,
    write_preprocess_artifacts,
)


STEP = 154
DEFAULT_STEP153_ROOT = Path("outputs") / "step153_official_tutorial_setup_parity"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step154_official_solver_prepost_pipeline"


def run_step154_official_solver_prepost_pipeline(
    step153_root: Path | str = DEFAULT_STEP153_ROOT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    grid: int = 48,
    z_cells: int | None = None,
    force: bool = False,
    write_preview: bool = True,
) -> dict[str, Any]:
    step153_root = Path(step153_root)
    output_dir = Path(output_dir)
    if force and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    case = compile_official_duct_flap_case(
        step153_root=step153_root,
        output_dir=output_dir,
        grid=int(grid),
        z_cells=z_cells,
    )
    geometry_masks = build_geometry_masks(case)
    boundary_masks = build_boundary_masks(case, geometry_masks)
    fsi_masks = build_fsi_interface_masks(case, geometry_masks)
    masks = {
        "geometry": geometry_masks,
        "boundary": boundary_masks,
        "fsi_interface": fsi_masks,
    }
    preprocess_report = write_preprocess_artifacts(case, masks, output_dir)
    postprocess_spec = build_postprocess_spec(case, output_dir)
    preview_report = {}
    if write_preview:
        preview_report = write_geometry_preview(case, masks, output_dir / "geometry_preview.png")
    else:
        (output_dir / "geometry_preview.png").write_bytes(_transparent_png_1x1())
        preview_report = {
            "step": STEP,
            "status": "geometry_preview_placeholder_written",
            "geometry_preview_path": _display_path(output_dir / "geometry_preview.png"),
            "validation_claim_allowed": False,
        }

    summary = _summary(case, preprocess_report, postprocess_spec, preview_report)
    _write_json(output_dir / "step154_summary.json", summary)
    _write_report(output_dir, summary)
    return summary


def _summary(
    case: dict[str, Any],
    preprocess_report: dict[str, Any],
    postprocess_spec: dict[str, Any],
    preview_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "official_solver_prepost_pipeline_ready",
        "compiled_case_ready_for_step155": True,
        "preprocessor_ready": bool(preprocess_report.get("preprocessor_ready")),
        "postprocessor_ready": postprocess_spec.get("status") == "postprocess_spec_ready",
        "official_tutorial_constants_loaded": bool(
            preprocess_report.get("official_tutorial_constants_loaded")
        ),
        "solver_input_case_written": bool(preprocess_report.get("solver_input_case_written")),
        "geometry_masks_written": bool(preprocess_report.get("geometry_masks_written")),
        "boundary_masks_written": bool(preprocess_report.get("boundary_masks_written")),
        "fsi_interface_masks_written": bool(preprocess_report.get("fsi_interface_masks_written")),
        "monitor_point_mapped": bool(preprocess_report.get("monitor_point_mapped")),
        "geometry_preview_written": bool(preview_report.get("status")),
        "step155_solver_run_allowed": True,
        "solver_run_executed": False,
        "fluent_run_executed": False,
        "step150_executed": False,
        "step148_helper_used_as_primary_runner": False,
        "official_monitor_loaded": False,
        "official_monitor_required_for_validation": True,
        "compiled_case": _display_path(Path(case["mask_artifacts"]["geometry_masks"]).parent / "compiled_case.json"),
        "compiled_case_path": case["mask_artifacts"]["geometry_masks"].replace(
            "geometry_masks.npz", "compiled_case.json"
        ),
        "source_step153_root": case["source_step153_root"],
        "source_step153_status": case["source_step153_status"],
        "solver_grid": case["solver_grid"],
        "monitor_spec": case["monitor_spec"],
        "mask_counts": preprocess_report.get("mask_counts", {}),
        "postprocess_spec_path": case["postprocess_spec_path"],
        "geometry_preview_path": preview_report.get("geometry_preview_path"),
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Step154 Official Solver Pre/Post Pipeline",
        "",
        "Step154 implemented the canonical official tutorial solver pre/post pipeline.",
        "",
        "It consumed Step153 setup-parity artifacts and generated a compiled case,",
        "geometry masks, boundary masks, FSI interface masks, material mapping,",
        "dimensionless mapping, postprocess specification, and geometry preview.",
        "",
        "Step154 did not run the FSI solver. Step154 did not run Fluent. Step154 did",
        "not use or fabricate official monitor data. Step154 did not run Step150 and",
        "does not make a validation claim.",
        "",
        "Step155 must consume:",
        "outputs/step154_official_solver_prepost_pipeline/compiled_case.json",
        "",
        "Step155 must not fall back to Step148 helper-driven implicit setup. The Step155",
        "solver runner must directly consume the compiled case and run the 50-step,",
        "0.0005 s official tutorial window.",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Compiled case ready for Step155: `{summary.get('compiled_case_ready_for_step155')}`",
        f"- Preprocessor ready: `{summary.get('preprocessor_ready')}`",
        f"- Postprocessor ready: `{summary.get('postprocessor_ready')}`",
        f"- Solver run executed: `{summary.get('solver_run_executed')}`",
        f"- Fluent run executed: `{summary.get('fluent_run_executed')}`",
        f"- Step150 executed: `{summary.get('step150_executed')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
    ]
    text = "\n".join(lines)
    (output_dir / "report.md").write_text(text, encoding="utf-8")
    if _is_default_output_dir(output_dir):
        doc_path = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "154" / "report.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(text, encoding="utf-8")


def _transparent_png_1x1() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00"
        b"\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display_path(path: Path | str) -> str:
    try:
        return str(Path(path).relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step153-root", type=Path, default=DEFAULT_STEP153_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--grid", type=int, default=48)
    parser.add_argument("--z-cells", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    preview = parser.add_mutually_exclusive_group()
    preview.add_argument("--write-preview", dest="write_preview", action="store_true", default=True)
    preview.add_argument("--no-preview", dest="write_preview", action="store_false")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step154_official_solver_prepost_pipeline(
        step153_root=args.step153_root,
        output_dir=args.output_dir,
        grid=args.grid,
        z_cells=args.z_cells,
        force=args.force,
        write_preview=args.write_preview,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
