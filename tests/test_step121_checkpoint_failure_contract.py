import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step121_lightweight_failure_detector_flags_density_and_population():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import detect_step121_lightweight_failure

    ok = detect_step121_lightweight_failure(
        {
            "step": 5,
            "rho_min": 0.98,
            "rho_max": 1.02,
            "max_v": 0.05,
            "f_min": 0.0,
            "F_min": 0.0,
            "stability_all_finite": True,
            "negative_population_fraction": 0.0,
        },
        {"mass_total": 10.0, "mass_initial": 10.0},
    )
    assert ok["failure_detected"] is False

    bad = detect_step121_lightweight_failure(
        {
            "step": 10,
            "rho_min": 0.50,
            "rho_max": 1.80,
            "max_v": 0.40,
            "f_min": -1.0e-3,
            "F_min": -2.0e-3,
            "stability_all_finite": True,
            "negative_population_fraction": 0.02,
        },
        {"mass_total": 7.0, "mass_initial": 10.0},
    )
    assert bad["failure_detected"] is True
    assert bad["first_failure_step"] == 10
    assert "rho_range" in bad["failure_reasons"]
    assert "negative_population_fraction" in bad["failure_reasons"]
    assert "mass_drift" in bad["failure_reasons"]


def test_step121_history_merge_deduplicates_by_step():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import merge_step121_history

    merged = merge_step121_history(
        [{"step": 0, "rho_min": 1.0}, {"step": 5, "rho_min": 0.99}],
        [{"step": 5, "rho_min": 0.98}, {"step": 10, "rho_min": 0.97}],
    )

    assert [row["step"] for row in merged] == [0, 5, 10]
    assert merged[1]["rho_min"] == 0.98


def test_step121_atomic_checkpoint_falls_back_to_previous_valid_file(tmp_path):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        load_latest_step121_checkpoint_payload,
        write_step121_checkpoint_payload,
    )

    checkpoint_root = tmp_path / "checkpoints"
    first = write_step121_checkpoint_payload(
        checkpoint_root,
        "row_a",
        5,
        {"step": 5, "mass_initial": 1.0},
        {"fluid": [{"step": 0}, {"step": 5}]},
    )
    write_step121_checkpoint_payload(
        checkpoint_root,
        "row_a",
        10,
        {"step": 10, "mass_initial": 1.0},
        {"fluid": [{"step": 0}, {"step": 5}, {"step": 10}]},
    )

    latest = checkpoint_root / "row_a" / "checkpoint_step_000010.json"
    latest.write_text("{corrupt", encoding="utf-8")

    loaded = load_latest_step121_checkpoint_payload(checkpoint_root, "row_a")

    assert first.exists()
    assert loaded["metadata"]["step"] == 5
    assert [row["step"] for row in loaded["history"]["fluid"]] == [0, 5]


def test_step121_failure_snapshot_writes_stats_and_runtime_npz(tmp_path):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import write_step121_failure_snapshot_arrays

    row_dir = tmp_path / "row"
    runtime_root = tmp_path / "runtime"
    rho = np.ones((4, 4, 4), dtype=np.float32)
    rho[2, 1, 3] = 1.8
    v = np.zeros((4, 4, 4, 3), dtype=np.float32)
    v[2, 1, 3, 0] = 0.4
    f = np.zeros((4, 4, 4, 19), dtype=np.float32)
    F = np.zeros((4, 4, 4, 19), dtype=np.float32)

    stats_path = write_step121_failure_snapshot_arrays(
        row_dir,
        runtime_root,
        "row_a",
        step=15,
        reason="rho_range",
        rho=rho,
        v=v,
        f=f,
        F=F,
    )

    payload = json.loads(stats_path.read_text(encoding="utf-8"))
    raw_path = Path(payload["runtime_npz_path"])

    assert stats_path.name == "failure_snapshot_step_000015_rho_range_stats.json"
    assert raw_path.is_file()
    assert payload["anomaly_cell"] == [2, 1, 3]
    assert payload["local_window"]["rho_max"] == 1.8
    assert payload["raw_arrays_committed_to_git"] is False
