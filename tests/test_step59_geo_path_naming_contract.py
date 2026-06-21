import json
from pathlib import Path

from src.mpm_lbm.evidence.geo_path_naming_audit import build_geo_path_naming_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step59_geo_path_naming_audit_passes_current_source():
    rows, summary = build_geo_path_naming_audit(ROOT)
    assert summary["geo_path_naming_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert int(summary["constructor_created_file_count"]) == 0
    by_grid = {int(row["n_grid"]): row for row in rows}
    assert by_grid[16]["actual_filename"] == "geo_all_fluid_16.dat"
    assert by_grid[32]["actual_filename"] == "geo_all_fluid_32.dat"
    assert by_grid[48]["actual_filename"] == "geo_all_fluid_48.dat"
    assert all(row["output_dir_exists_after"] is False for row in rows)
    assert all(not str(row["geo_path"]).startswith(("C:", "D:")) for row in rows)


def test_step59_geo_path_naming_artifact_passes():
    payload = read_json("outputs/step59_geo_path_naming_audit/geo_path_naming_audit.json")
    summary = payload["summary"]
    assert summary["geo_path_naming_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert all(row["pass"] is True for row in payload["rows"])
    assert all(not str(row["geo_path"]).startswith(("C:", "D:")) for row in payload["rows"])


def test_step59_fsidriver_uses_n_grid_in_geo_path_source():
    source = (ROOT / "src/mpm_lbm/sim/drivers/fsi_driver.py").read_text(encoding="utf-8")
    assert 'f"geo_all_fluid_{self.config.n_grid}.dat"' in source
    assert '"geo_all_fluid_32.dat"' not in source


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
