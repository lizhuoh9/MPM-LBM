import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_log(relative_path):
    raw = (ROOT / relative_path).read_bytes()
    for encoding in ("utf-8", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="ignore")


def read_json(relative_path):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path):
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def as_float(row, key):
    return float(row[key])


def as_int(row, key):
    return int(float(row[key]))


def assert_finite_row(row, excluded=()):
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        numeric = float(value)
        assert math.isfinite(numeric), f"{key} is not finite"


def assert_area_scale_range(row):
    assert math.isfinite(as_float(row, "area_scale_min"))
    assert math.isfinite(as_float(row, "area_scale_max"))
    assert 0.25 <= as_float(row, "area_scale_min")
    assert as_float(row, "area_scale_min") <= as_float(row, "area_scale_max")
    assert as_float(row, "area_scale_max") <= 2.0


def assert_step19_stable(row, require_link_area=False):
    assert_finite_row(
        row,
        excluded=("case", "mode", "transfer_mode", "reaction_transfer_mode", "geometry_type", "stable", "well_behaved", "notes"),
    )
    assert as_bool(row["stable"])
    assert as_float(row, "rho_min_global") > 0.95
    assert as_float(row, "rho_max_global") < 1.05
    assert as_float(row, "lbm_max_v_global") < 0.1
    assert as_float(row, "mpm_min_J_global") > 0.0
    assert as_float(row, "mpm_max_speed_global") < 10.0
    assert as_float(row, "cell_force_max_norm") == 0.0
    assert as_int(row, "bb_link_count_min") > 0
    if require_link_area:
        assert row["reaction_transfer_mode"] == "link_area_experimental"
        assert as_int(row, "active_reaction_particle_count_min") > 0
        assert_area_scale_range(row)


def test_step19_required_artifacts_exist():
    required_paths = [
        "configs/step19_long_box_48_link_area.json",
        "configs/step19_long_squid_proxy_48_link_area.json",
        "configs/step19_feasibility_64_link_area_box.json",
        "configs/step19_compare_64_engineering_vs_link_area.json",
        "configs/step19_compare_48_long_engineering_vs_link_area.json",
        "baseline_tests/step19_common.py",
        "baseline_tests/run_step19_long_box_48_link_area.py",
        "baseline_tests/run_step19_long_squid_proxy_48_link_area.py",
        "baseline_tests/run_step19_feasibility_64_link_area.py",
        "baseline_tests/run_step19_compare_64_engineering_vs_link_area.py",
        "baseline_tests/run_step19_compare_48_long_engineering_vs_link_area.py",
        "baseline_tests/run_step19_regression_step18.py",
        "baseline_tests/run_step19_long_run_summary.py",
        "baseline_tests/run_step19_artifact_manifest.py",
        "docs/18_link_area_long_run.md",
        "STEP19_LINK_AREA_LONG_RUN_REPORT.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step19_source_defaults_and_boundaries_are_preserved():
    fsi_config = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    fsi_driver = read_text("src/mpm_lbm/sim/drivers/fsi_driver.py")
    link_area = read_text("src/mpm_lbm/sim/coupling/link_area.py")

    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config
    assert "reaction_transfer_mode == \"link_area_experimental\"" in fsi_config
    assert "coupling_mode != \"moving_boundary\"" in fsi_config

    assert "reaction_transfer_mode == \"engineering\"" in fsi_driver
    assert "reaction_transfer_mode == \"link_area_experimental\"" in fsi_driver
    assert "self.mb_coupler = MovingBoundaryFSICoupler3D" in fsi_driver
    assert "self.link_area_coupler = LinkAreaMovingBoundaryCoupler3D" in fsi_driver
    assert "self.lbm.step_moving_bounceback()" in fsi_driver

    required_link_area_tokens = [
        "class LinkAreaMovingBoundaryCoupler3D",
        "raw_area_scale = numerator / denominator",
        "area_scale = float(np.clip(raw_area_scale, self.area_scale_min, self.area_scale_max))",
        "sampled_hydro_lbm",
        "* self.force_density_scale_lbm_to_norm",
        "* self.reaction_scale",
        "* scale",
        "solid.grid_f_ext[I]",
    ]
    missing = [token for token in required_link_area_tokens if token not in link_area]
    assert missing == []


def test_step19_configs_match_contract_and_disable_heavy_exports():
    long_box = read_json("configs/step19_long_box_48_link_area.json")
    long_squid = read_json("configs/step19_long_squid_proxy_48_link_area.json")
    feasibility = read_json("configs/step19_feasibility_64_link_area_box.json")
    compare64 = read_json("configs/step19_compare_64_engineering_vs_link_area.json")
    compare48 = read_json("configs/step19_compare_48_long_engineering_vs_link_area.json")

    experimental = [long_box, long_squid, feasibility]
    for config in experimental:
        assert config["coupling_mode"] == "moving_boundary"
        assert config["reaction_transfer_mode"] == "link_area_experimental"
        assert config["link_area_policy"] == "inverse_length"
        assert float(config["link_area_scale_min"]) == 0.25
        assert float(config["link_area_scale_max"]) == 2.0
        assert config["write_vtk"] is False
        assert config["write_particles"] is False

    assert long_box["geometry_type"] == "box"
    assert int(long_box["n_grid"]) == 48
    assert int(long_box["n_particles"]) == 13824
    assert int(long_box["n_lbm_steps"]) >= 50
    assert int(long_box["mpm_substeps_per_lbm_step"]) >= 10

    assert long_squid["geometry_type"] == "squid_proxy"
    assert long_squid["geometry_config_path"] == "configs/step13_squid_proxy_geometry.json"
    assert int(long_squid["n_grid"]) == 48
    assert int(long_squid["n_particles"]) == 4096
    assert int(long_squid["n_lbm_steps"]) >= 30

    assert int(feasibility["n_grid"]) == 64
    assert int(feasibility["n_particles"]) == 32768
    assert int(feasibility["n_lbm_steps"]) >= 5

    assert compare64["reaction_transfer_mode"] == "engineering"
    assert compare64["write_vtk"] is False
    assert compare64["write_particles"] is False

    for key in ("box_48", "squid_proxy_48"):
        section = compare48[key]
        assert section["coupling_mode"] == "moving_boundary"
        assert section["write_vtk"] is False
        assert section["write_particles"] is False


def test_step19_logs_record_success_markers():
    expected_markers = {
        "logs/step19_long_box_48_link_area.log": "[OK] Step 19 48^3 box link-area long-run finished",
        "logs/step19_long_squid_proxy_48_link_area.log": "[OK] Step 19 48^3 squid_proxy link-area long-run finished",
        "logs/step19_feasibility_64_link_area.log": "[OK] Step 19 64^3 link-area feasibility finished",
        "logs/step19_compare_64_engineering_vs_link_area.log": "[OK] Step 19 64^3 engineering vs link-area comparison finished",
        "logs/step19_compare_48_long_engineering_vs_link_area.log": "[OK] Step 19 48^3 long engineering vs link-area comparison finished",
        "logs/step19_regression_step18.log": "[OK] Step 19 Step 18 regression finished",
        "logs/step19_long_run_summary.log": "[OK] Step 19 long-run summary finished",
        "logs/step19_artifact_manifest.log": "[OK] Step 19 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step19_long_link_area_runs_are_valid():
    checks = [
        ("outputs/step19_long_box_48_link_area/long_run_summary.json", 48, 50, 500),
        ("outputs/step19_long_squid_proxy_48_link_area/long_run_summary.json", 48, 30, 300),
    ]
    for path, n_grid, min_steps, min_substeps in checks:
        row = read_json(path)
        assert row["reaction_transfer_mode"] == "link_area_experimental"
        assert int(row["n_grid"]) == n_grid
        assert int(row["completed_lbm_steps"]) >= min_steps
        assert int(row["total_mpm_substeps"]) >= min_substeps
        assert_step19_stable(row, require_link_area=True)

        out_dir = str(Path(path).parent).replace(str(ROOT) + "\\", "").replace("\\", "/")
        payload = np.load(ROOT / out_dir / "link_area_timeseries.npz")
        assert "area_scale" in payload.files
        assert "raw_area_scale" in payload.files


def test_step19_64_link_area_feasibility_is_valid():
    row = read_json("outputs/step19_feasibility_64_link_area/long_run_summary.json")
    assert row["reaction_transfer_mode"] == "link_area_experimental"
    assert int(row["n_grid"]) == 64
    assert int(row["n_particles"]) == 32768
    assert int(row["completed_lbm_steps"]) >= 5
    assert int(row["total_mpm_substeps"]) >= 25
    assert_step19_stable(row, require_link_area=True)

    rows = read_csv_rows("outputs/step19_feasibility_64_link_area/box_64_link_area_results.csv")
    assert len(rows) == 1
    assert rows[0]["case"] == "box_64_link_area_feasibility"
    assert rows[0]["reaction_transfer_mode"] == "link_area_experimental"


def test_step19_engineering_vs_link_area_comparisons_are_valid():
    checks = [
        (
            "outputs/step19_compare_64_engineering_vs_link_area/comparison_64.csv",
            {("box_64", "engineering"), ("box_64", "link_area_experimental")},
        ),
        (
            "outputs/step19_compare_48_long_engineering_vs_link_area/comparison_48_long.csv",
            {
                ("box_48", "engineering"),
                ("box_48", "link_area_experimental"),
                ("squid_proxy_48", "engineering"),
                ("squid_proxy_48", "link_area_experimental"),
            },
        ),
    ]
    for path, expected in checks:
        rows = read_csv_rows(path)
        found = {(row["case"], row["reaction_transfer_mode"]) for row in rows}
        assert expected.issubset(found)
        for row in rows:
            assert_step19_stable(row, require_link_area=row["reaction_transfer_mode"] == "link_area_experimental")
            if row["reaction_transfer_mode"] == "engineering":
                assert as_float(row, "area_scale_final") == 1.0


def test_step19_regression_summary_and_manifest_are_valid():
    regression_rows = read_csv_rows("outputs/step19_regression_step18/regression_results.csv")
    expected_cases = {
        "step18_sanity_regression",
        "step18_box_48_experimental_regression",
        "engineering_default_regression",
    }
    assert expected_cases.issubset({row["case"] for row in regression_rows})
    for row in regression_rows:
        assert_step19_stable(row, require_link_area=row["reaction_transfer_mode"] == "link_area_experimental")

    summary_rows = read_csv_rows("outputs/step19_long_run_summary/step19_summary.csv")
    required_summary_cases = {
        "box_48_link_area_long",
        "squid_proxy_48_link_area_long",
        "box_64_link_area_feasibility",
        "engineering_vs_link_area_64",
        "engineering_vs_link_area_48",
        "step18_regression",
    }
    assert required_summary_cases.issubset({row["summary_case"] for row in summary_rows})
    assert all(as_bool(row["stable"]) for row in summary_rows)

    artifact_summary = read_json("outputs/step19_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert (ROOT / "logs/step19_pytest.log").is_file()


def test_step19_docs_report_scope_and_avoid_overclaims():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/10_performance_memory.md",
        "docs/16_link_area_momentum_accounting.md",
        "docs/17_experimental_link_area_transfer.md",
        "docs/18_link_area_long_run.md",
        "STEP19_LINK_AREA_LONG_RUN_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())
    required_scope = [
        "Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "LinkAreaMovingBoundaryCoupler3D formula is unchanged.",
        "MovingBoundaryFSICoupler3D is unchanged.",
        "The link-area transfer remains experimental and uses a bounded global area_scale.",
        "This is not final strict momentum-conserving sharp-interface FSI.",
        "squid_proxy is procedural and not real squid validation.",
    ]
    missing = [phrase for phrase in required_scope if phrase not in combined]
    assert missing == []

    forbidden_claims = [
        "strict momentum-conserving FSI is complete",
        "real squid simulation is validated",
        "validated squid swimming",
        "production-ready sharp-interface FSI",
        "final local surface-area reconstruction",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined]
    assert offenders == []


def test_step19_report_acceptance_complete():
    report = read_text("STEP19_LINK_AREA_LONG_RUN_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. 48^3 Box Link-Area Long-Run Result",
        "## 5. 48^3 Procedural Squid Proxy Link-Area Long-Run Result",
        "## 6. 64^3 Link-Area Feasibility Result",
        "## 7. 64^3 Engineering Vs Link-Area Comparison Result",
        "## 8. 48^3 Long Engineering Vs Link-Area Comparison Result",
        "## 9. Step 18 Regression Result",
        "## 10. Long-Run Summary Result",
        "## 11. Artifact Manifest Summary",
        "## 12. Verification Commands",
        "## 13. GitHub Sync Information",
        "## 14. Acceptance Checklist",
        "## 15. Decision For Step 20",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] 48^3 box link_area_experimental long-run completes",
        "- [x] 48^3 squid_proxy link_area_experimental long-run completes",
        "- [x] 64^3 link_area_experimental feasibility completes",
        "- [x] 64^3 engineering vs link-area comparison completes",
        "- [x] 48^3 long engineering vs link-area comparison completes",
        "- [x] Step 18 regression completes",
        "- [x] area_scale is finite for all experimental rows",
        "- [x] area_scale stays within configured bounds",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] link_area_experimental remains opt-in",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step19_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Git pre-push pytest hook passes",
        "- [x] git diff --check passes",
        "- [x] Step 19 artifacts are pushed to GitHub origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
