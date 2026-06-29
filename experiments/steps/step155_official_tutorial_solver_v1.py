"""Step155 official tutorial solver V1 runner.

The implementation path instantiates FSIDriver3D inside the Step155 solver
adapter instead of routing through earlier Step148/Step153 helper runners.
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

from src.mpm_lbm.solvers.official_duct_flap_solver import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_RAW_OUTPUT_DIR,
    run_official_tutorial_solver_v1,
)


DEFAULT_CASE = Path("outputs") / "step154_official_solver_prepost_pipeline" / "compiled_case.json"


def _ensure_taichi_cpu(cpu_max_num_threads: int) -> None:
    ti.init(arch=ti.cpu, cpu_max_num_threads=int(cpu_max_num_threads))


def _parse_target_u_lbm(value: str) -> tuple[float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("--target-u-lbm must contain three comma-separated floats")
    return tuple(float(part) for part in parts)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--raw-output-dir", type=Path, default=DEFAULT_RAW_OUTPUT_DIR)
    parser.add_argument("--n-particles", type=int, default=1024)
    parser.add_argument("--target-u-lbm", type=_parse_target_u_lbm, default=(0.02, 0.0, 0.0))
    parser.add_argument("--snapshot-interval", type=int, default=5)
    parser.add_argument("--monitor-interval", type=int, default=1)
    parser.add_argument("--taichi-arch", choices=("cpu",), default="cpu")
    parser.add_argument("--cpu-max-num-threads", type=int, default=1)
    parser.add_argument("--allow-test-grid-override", action="store_true")
    parser.add_argument("--test-grid", type=int, default=None)
    parser.add_argument("--test-n-steps", type=int, default=None)
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
        summary = run_official_tutorial_solver_v1(
            compiled_case_path=args.case,
            output_dir=args.output_dir,
            raw_output_dir=args.raw_output_dir,
            force=args.force,
            n_particles=args.n_particles,
            target_u_lbm=args.target_u_lbm,
            snapshot_interval=args.snapshot_interval,
            monitor_interval=args.monitor_interval,
            allow_test_grid_override=args.allow_test_grid_override,
            test_grid=args.test_grid,
            test_n_steps=args.test_n_steps,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Step155 failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
