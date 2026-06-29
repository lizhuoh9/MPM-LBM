import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step150_missing_official_monitor_blocks_without_metrics(tmp_path):
    import experiments.steps.step150_official_monitor_intake_and_error_localization as step150

    solver = tmp_path / "solver_monitor.csv"
    write_solver_monitor(solver, [0.0, 0.5, 1.0])

    summary = step150.run_step150_official_monitor_intake(
        official_monitor=tmp_path / "missing" / "official_monitor.csv",
        solver_monitor=solver,
        solver_force_monitor=solver,
        solver_summary=None,
        output_dir=tmp_path / "out",
        force=True,
    )

    assert summary["step"] == 150
    assert summary["status"] == "missing_official_monitor"
    assert summary["official_reference_loaded"] is False
    assert summary["solver_monitor_loaded"] is True
    assert summary["solver_monitor_rows"] == 3
    assert summary["step149_comparison_ran"] is False
    assert summary["error_metrics_present"] is False
    assert summary["solver_bug_hypotheses_present"] is False
    assert summary["next_code_fix_step_identified"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert (tmp_path / "out" / "official_monitor_intake_summary.json").is_file()
    assert (tmp_path / "out" / "step150_decision_summary.json").is_file()


def test_step150_missing_solver_monitor_blocks_without_metrics(tmp_path):
    import experiments.steps.step150_official_monitor_intake_and_error_localization as step150

    official = tmp_path / "official_monitor.csv"
    write_official_monitor(official, [0.0, 0.5, 1.0])

    summary = step150.run_step150_official_monitor_intake(
        official_monitor=official,
        solver_monitor=tmp_path / "missing_solver.csv",
        solver_force_monitor=tmp_path / "missing_solver.csv",
        solver_summary=None,
        output_dir=tmp_path / "out",
        force=True,
    )

    assert summary["status"] == "missing_solver_monitor"
    assert summary["official_reference_loaded"] is True
    assert summary["solver_monitor_loaded"] is False
    assert summary["official_monitor_hash"]
    assert summary["official_monitor_committed"] is False
    assert summary["step149_comparison_ran"] is False
    assert summary["error_metrics_present"] is False
    assert summary["next_code_fix_step_identified"] is False


def test_step150_official_schema_requires_time_s(tmp_path):
    summary = run_invalid_schema_fixture(
        tmp_path,
        [{"flap_tip_total_displacement_m": 0.0}, {"flap_tip_total_displacement_m": 1.0}],
    )

    assert summary["status"] == "schema_invalid"
    assert summary["schema_valid"] is False
    assert summary["step149_comparison_ran"] is False
    assert "time_s" in " ".join(summary["schema_errors"])
    assert summary["error_metrics_present"] is False


def test_step150_official_schema_requires_displacement(tmp_path):
    summary = run_invalid_schema_fixture(
        tmp_path,
        [{"time_s": 0.0, "fluid_force_magnitude_n": 0.0}, {"time_s": 1.0, "fluid_force_magnitude_n": 1.0}],
    )

    assert summary["status"] == "schema_invalid"
    assert summary["schema_valid"] is False
    assert summary["step149_comparison_ran"] is False
    assert "displacement" in " ".join(summary["schema_errors"]).lower()
    assert summary["solver_bug_hypotheses_present"] is False


def test_step150_official_schema_rejects_nonmonotonic_time(tmp_path):
    summary = run_invalid_schema_fixture(
        tmp_path,
        [
            {"time_s": 0.0, "flap_tip_total_displacement_m": 0.0},
            {"time_s": 1.0, "flap_tip_total_displacement_m": 1.0},
            {"time_s": 0.5, "flap_tip_total_displacement_m": 0.5},
        ],
    )

    assert summary["status"] == "schema_invalid"
    assert summary["step149_comparison_ran"] is False
    assert any("monotonic" in error for error in summary["schema_errors"])
    assert summary["next_code_fix_step_identified"] is False


def test_step150_no_time_overlap_blocks_before_step149_comparison(tmp_path):
    import experiments.steps.step150_official_monitor_intake_and_error_localization as step150

    official = tmp_path / "official_monitor.csv"
    solver = tmp_path / "solver_monitor.csv"
    write_official_monitor(official, [10.0, 11.0, 12.0])
    write_solver_monitor(solver, [0.0, 0.5, 1.0])

    summary = step150.run_step150_official_monitor_intake(
        official_monitor=official,
        solver_monitor=solver,
        solver_force_monitor=solver,
        solver_summary=None,
        output_dir=tmp_path / "out",
        force=True,
    )

    assert summary["status"] == "no_time_overlap"
    assert summary["official_reference_loaded"] is True
    assert summary["solver_monitor_loaded"] is True
    assert summary["step149_comparison_ran"] is False
    assert summary["error_metrics_present"] is False
    assert summary["solver_bug_hypotheses_present"] is False


def test_step150_synthetic_monitor_generates_metrics_hypotheses_and_step151_target(tmp_path):
    import experiments.steps.step150_official_monitor_intake_and_error_localization as step150

    official = tmp_path / "official_monitor.csv"
    solver = tmp_path / "solver_monitor.csv"
    write_official_monitor(official, [0.0, 0.5, 1.0], displacements=[0.0, 2.0, 0.0], forces=[0.0, 10.0, 0.0])
    write_solver_monitor(solver, [0.0, 0.5, 1.0], displacements=[0.0, 1.0, 0.2], forces=[0.0, 2.0, 0.0])

    out_dir = tmp_path / "out"
    summary = step150.run_step150_official_monitor_intake(
        official_monitor=official,
        solver_monitor=solver,
        solver_force_monitor=solver,
        solver_summary=None,
        output_dir=out_dir,
        force=True,
    )

    assert summary["status"] == "error_localization_complete"
    assert summary["official_reference_loaded"] is True
    assert summary["solver_monitor_loaded"] is True
    assert len(summary["official_monitor_hash"]) == 64
    assert summary["official_monitor_committed"] is False
    assert summary["official_monitor_rows"] == 3
    assert summary["solver_monitor_rows"] == 3
    assert summary["aligned_sample_count"] == 3
    assert summary["step149_comparison_ran"] is True
    assert summary["error_metrics_present"] is True
    assert summary["solver_bug_hypotheses_present"] is True
    assert summary["top_bug_category"]
    assert summary["next_code_fix_step_identified"] is True
    assert summary["recommended_next_step"] == 151
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False

    displacement = read_json(out_dir / "displacement_error_metrics.json")
    hypotheses = read_json(out_dir / "solver_bug_hypotheses.json")
    assert displacement["status"] == "computed"
    assert hypotheses["hypotheses"]
    assert (out_dir / "aligned_monitor_comparison.csv").is_file()
    assert (out_dir / "official_monitor_private_hash_report.json").is_file()


def run_invalid_schema_fixture(tmp_path: Path, official_rows: list[dict]):
    import experiments.steps.step150_official_monitor_intake_and_error_localization as step150

    official = tmp_path / "official_monitor.csv"
    solver = tmp_path / "solver_monitor.csv"
    write_csv(official, official_rows)
    write_solver_monitor(solver, [0.0, 0.5, 1.0])
    return step150.run_step150_official_monitor_intake(
        official_monitor=official,
        solver_monitor=solver,
        solver_force_monitor=solver,
        solver_summary=None,
        output_dir=tmp_path / "out",
        force=True,
    )


def write_official_monitor(path: Path, times: list[float], displacements=None, forces=None):
    displacements = displacements if displacements is not None else [float(index) for index, _ in enumerate(times)]
    forces = forces if forces is not None else [0.0 for _ in times]
    rows = [
        {
            "time_s": time_s,
            "flap_tip_total_displacement_m": displacement,
            "fluid_force_magnitude_n": force,
        }
        for time_s, displacement, force in zip(times, displacements, forces)
    ]
    write_csv(path, rows)


def write_solver_monitor(path: Path, times: list[float], displacements=None, forces=None):
    displacements = displacements if displacements is not None else [float(index) for index, _ in enumerate(times)]
    forces = forces if forces is not None else [0.0 for _ in times]
    rows = [
        {
            "time_s": time_s,
            "step": index,
            "flap_tip_total_displacement_m": displacement,
            "flap_tip_x_displacement_m": 0.0,
            "flap_tip_y_displacement_m": displacement,
            "flap_tip_velocity_m_per_s": 0.0,
            "fluid_force_x_n": 0.0,
            "fluid_force_y_n": force,
            "fluid_force_magnitude_n": force,
        }
        for index, (time_s, displacement, force) in enumerate(zip(times, displacements, forces))
    ]
    write_csv(path, rows)


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
