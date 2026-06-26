import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class _ArrayField:
    def __init__(self, value):
        self.value = np.array(value)

    def to_numpy(self):
        return np.array(self.value)

    def from_numpy(self, value):
        self.value = np.array(value)


class _FakeCheckpointLbm:
    def __init__(self, *, nx=4, ny=3, nz=3):
        self.f = _ArrayField(np.zeros((nx, ny, nz, 19), dtype=np.float32))
        self.F = _ArrayField(np.zeros((nx, ny, nz, 19), dtype=np.float32))
        self.rho = _ArrayField(np.ones((nx, ny, nz), dtype=np.float32))
        self.v = _ArrayField(np.zeros((nx, ny, nz, 3), dtype=np.float32))
        self.solid = _ArrayField(np.zeros((nx, ny, nz), dtype=np.int8))
        self.static_solid = _ArrayField(np.zeros((nx, ny, nz), dtype=np.int8))
        self.stats = {
            "rho_clip_count_run": 2,
            "velocity_clip_count_run": 3,
            "noneq_clip_count_run": 4,
            "population_floor_count_run": 5,
            "reconstructed_population_count_run": 19,
            "mass_balance_correction_count_run": 7,
            "mass_balance_correction_abs_sum_run": 0.125,
            "unknown_population_delta_abs_sum_run": 0.25,
        }

    def get_open_boundary_limiter_stats(self):
        return dict(self.stats)

    def set_open_boundary_limiter_run_counters(
        self,
        rho_clip_count,
        velocity_clip_count,
        noneq_clip_count,
        population_floor_count,
        reconstructed_population_count,
    ):
        self.stats["rho_clip_count_run"] = int(rho_clip_count)
        self.stats["velocity_clip_count_run"] = int(velocity_clip_count)
        self.stats["noneq_clip_count_run"] = int(noneq_clip_count)
        self.stats["population_floor_count_run"] = int(population_floor_count)
        self.stats["reconstructed_population_count_run"] = int(reconstructed_population_count)
        self.stats["mass_balance_correction_count_run"] = 0
        self.stats["mass_balance_correction_abs_sum_run"] = 0.0
        self.stats["unknown_population_delta_abs_sum_run"] = 0.0

    def set_open_boundary_repair_run_counters(
        self,
        mass_balance_correction_count,
        mass_balance_correction_abs_sum,
        unknown_population_delta_abs_sum,
    ):
        self.stats["mass_balance_correction_count_run"] = int(mass_balance_correction_count)
        self.stats["mass_balance_correction_abs_sum_run"] = float(mass_balance_correction_abs_sum)
        self.stats["unknown_population_delta_abs_sum_run"] = float(unknown_population_delta_abs_sum)


def _spec():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    return Step120RunSpec(
        name="step129_repair_counter_checkpoint_contract",
        nx=4,
        ny=3,
        nz=3,
        n_steps=2,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=1,
        open_boundary_semantics="regularized_mass_balanced_pressure_outlet",
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=2,
        allow_large_real_run_without_flag=True,
        row_role="repair_candidate_48",
    )


def test_step129_checkpoint_metadata_includes_repair_counters(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import write_step120_checkpoint

    spec = _spec()
    checkpoint = write_step120_checkpoint(
        _FakeCheckpointLbm(),
        spec,
        tmp_path / "checkpoints",
        step=1,
        mass_initial=36.0,
        records=[],
        stability_records=[],
    )

    metadata = json.loads(checkpoint.with_suffix(".json").read_text(encoding="utf-8"))
    counters = metadata["limiter_counters"]

    assert metadata["limiter_counter_source"] == "actual_open_boundary_kernel_counters"
    assert counters["mass_balance_correction_count"] == 7
    assert counters["mass_balance_correction_abs_sum"] == 0.125
    assert counters["unknown_population_delta_abs_sum"] == 0.25


def test_step129_checkpoint_restore_preserves_repair_run_counters(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        restore_latest_step120_checkpoint_with_history,
        write_step120_checkpoint,
    )

    spec = _spec()
    checkpoint_root = tmp_path / "checkpoints"
    write_step120_checkpoint(
        _FakeCheckpointLbm(),
        spec,
        checkpoint_root,
        step=1,
        mass_initial=36.0,
        records=[],
        stability_records=[],
    )

    restored_lbm = _FakeCheckpointLbm()
    restored_lbm.stats["mass_balance_correction_count_run"] = 0
    restored_lbm.stats["mass_balance_correction_abs_sum_run"] = 0.0
    restored_lbm.stats["unknown_population_delta_abs_sum_run"] = 0.0

    restored = restore_latest_step120_checkpoint_with_history(restored_lbm, spec, checkpoint_root)
    stats = restored_lbm.get_open_boundary_limiter_stats()

    assert restored is not None
    assert restored[0] == 1
    assert stats["rho_clip_count_run"] == 2
    assert stats["reconstructed_population_count_run"] == 19
    assert stats["mass_balance_correction_count_run"] == 7
    assert stats["mass_balance_correction_abs_sum_run"] == 0.125
    assert stats["unknown_population_delta_abs_sum_run"] == 0.25
