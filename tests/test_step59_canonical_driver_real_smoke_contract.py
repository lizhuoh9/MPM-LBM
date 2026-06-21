import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_smoke_audit import build_canonical_driver_smoke_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step59_canonical_driver_smoke_audit_passes_committed_artifacts():
    rows, summary = build_canonical_driver_smoke_audit(ROOT)
    assert summary["canonical_driver_smoke_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert int(summary["driver_run_called_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["pass"] is True for row in rows)


def test_step59_canonical_driver_smoke_matrix_artifact_passes():
    payload = read_json("outputs/step59_canonical_driver_smoke_matrix/smoke_matrix.json")
    summary = payload["summary"]
    assert summary["canonical_driver_smoke_matrix_pass"] is True
    assert int(summary["row_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["driver_run_called_count"]) == 3
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["driver_run_called"] is True for row in payload["rows"])
    assert all(row["stable"] is True for row in payload["rows"])
    assert all(row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver" for row in payload["rows"])
    assert all(row["legacy_driver_module_used_as_implementation"] is False for row in payload["rows"])


def test_step59_required_driver_run_outputs_exist_and_are_lightweight():
    policy = read_json("configs/step59_smoke_acceptance_policy.json")
    allowed = set(policy["allowed_driver_run_files"])
    for row_name in policy["required_row_names"]:
        run_dir = ROOT / "outputs" / "step59_driver_runs" / row_name
        assert run_dir.is_dir()
        actual = {path.name for path in run_dir.iterdir() if path.is_file()}
        assert actual == allowed
        assert (run_dir / "geo_all_fluid_16.dat").is_file()
        assert not any(path.suffix.lower() == ".vtr" for path in run_dir.rglob("*"))
        assert not any(path.suffix.lower() == ".npy" and "particle" in path.name.lower() for path in run_dir.rglob("*"))


def test_step59_smoke_quality_artifact_passes():
    payload = read_json("outputs/step59_canonical_driver_smoke_quality/smoke_quality.json")
    summary = payload["summary"]
    assert summary["canonical_driver_smoke_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert all(row["pass"] is True for row in payload["rows"])


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
