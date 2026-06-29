"""Step157 official subcycled flow-development repair runner.

This path uses FSIDriver3D through the Step157 subcycled solver adapter.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Sequence

import taichi as ti

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mpm_lbm.solvers.official_subcycled_flow_solver import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_RAW_OUTPUT_DIR,
    run_step157_subcycled_flow_repair,
)


DEFAULT_CASE = Path("outputs") / "step154_official_solver_prepost_pipeline" / "compiled_case.json"
DEFAULT_STEP155_ROOT = Path("outputs") / "step155_official_tutorial_solver_v1"
DEFAULT_STEP156_ROOT = Path("outputs") / "step156_official_tutorial_postprocess_and_acceptance"


def _ensure_taichi_cpu(cpu_max_num_threads: int) -> None:
    ti.init(arch=ti.cpu, cpu_max_num_threads=int(cpu_max_num_threads))


def _parse_target_u_lbm(value: str) -> tuple[float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("--target-u-lbm must contain three comma-separated floats")
    return tuple(float(part) for part in parts)


def _parse_snapshot_steps(value: str) -> tuple[int, ...]:
    if not value.strip():
        raise argparse.ArgumentTypeError("--snapshot-official-steps cannot be empty")
    try:
        steps = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--snapshot-official-steps must contain integers") from exc
    if any(step < 0 for step in steps):
        raise argparse.ArgumentTypeError("--snapshot-official-steps cannot contain negative steps")
    return steps


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--step155-root", type=Path, default=DEFAULT_STEP155_ROOT)
    parser.add_argument("--step156-root", type=Path, default=DEFAULT_STEP156_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--raw-output-dir", type=Path, default=DEFAULT_RAW_OUTPUT_DIR)
    parser.add_argument("--n-particles", type=int, default=1024)
    parser.add_argument("--target-u-lbm", type=_parse_target_u_lbm, default=(0.02, 0.0, 0.0))
    parser.add_argument("--lbm-substeps-per-fsi-step", type=int, default=None)
    parser.add_argument("--snapshot-official-steps", type=_parse_snapshot_steps, default=(0, 5, 10, 20, 30, 40, 50))
    parser.add_argument("--tail-fraction", type=float, default=0.2)
    parser.add_argument("--max-wall-seconds", type=float, default=None)
    parser.add_argument("--taichi-arch", choices=("cpu",), default="cpu")
    parser.add_argument("--cpu-max-num-threads", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    del args.taichi_arch
    try:
        warnings.filterwarnings(
            "ignore",
            message="Taichi matrices/vectors with 19x19.*",
            category=UserWarning,
        )
        _ensure_taichi_cpu(args.cpu_max_num_threads)
        summary = run_step157_subcycled_flow_repair(
            compiled_case_path=args.case,
            step155_root=args.step155_root,
            step156_root=args.step156_root,
            output_dir=args.output_dir,
            raw_output_dir=args.raw_output_dir,
            force=args.force,
            n_particles=args.n_particles,
            target_u_lbm=args.target_u_lbm,
            lbm_substeps_per_fsi_step=args.lbm_substeps_per_fsi_step,
            snapshot_official_steps=args.snapshot_official_steps,
            tail_fraction=args.tail_fraction,
            max_wall_seconds=args.max_wall_seconds,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Step157 failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
