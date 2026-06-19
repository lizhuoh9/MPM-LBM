import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_csv_rows(relative_path):
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(relative_path):
    return json.loads(read_text(relative_path))


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def as_float(row, key):
    return float(row[key])


def assert_finite_row(row, excluded=()):
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        numeric = float(value)
        assert math.isfinite(numeric), f"{key} is not finite"


def assert_stable_rows(rows):
    for row in rows:
        if not as_bool(row.get("stable", False)):
            continue
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0


def test_step15_required_artifacts_exist():
    required_paths = [
        "src/momentum_accounting.py",
        "src/calibration.py",
        "configs/step15_mb_calibration_box_32.json",
        "configs/step15_mb_force_cap_box_48.json",
        "configs/step15_mb_calibration_squid_proxy_48.json",
        "configs/step15_mb_recommended_box_48.json",
        "configs/step15_mb_recommended_squid_proxy_48.json",
        "baseline_tests/run_step15_momentum_accounting_sanity.py",
        "baseline_tests/run_step15_reaction_scale_sweep_box_32.py",
        "baseline_tests/run_step15_force_cap_sweep_box_48.py",
        "baseline_tests/run_step15_squid_proxy_calibrated_window.py",
        "baseline_tests/run_step15_calibrated_vs_original_comparison.py",
        "baseline_tests/run_step15_artifact_manifest.py",
        "logs/step15_momentum_accounting.log",
        "logs/step15_reaction_scale_sweep_box_32.log",
        "logs/step15_force_cap_sweep_box_48.log",
        "logs/step15_squid_proxy_calibrated_window.log",
        "logs/step15_calibrated_vs_original.log",
        "logs/step15_artifact_manifest.log",
        "logs/step15_pytest.log",
        "outputs/step15_momentum_accounting/accounting_timeseries.csv",
        "outputs/step15_momentum_accounting/accounting_timeseries.npz",
        "outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.csv",
        "outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.npz",
        "outputs/step15_force_cap_sweep_box_48/force_cap_sweep.csv",
        "outputs/step15_force_cap_sweep_box_48/force_cap_sweep.npz",
        "outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.csv",
        "outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.npz",
        "outputs/step15_calibrated_vs_original/comparison.csv",
        "outputs/step15_calibrated_vs_original/comparison.npz",
        "outputs/step15_artifact_manifest/artifact_summary.json",
        "docs/14_moving_boundary_calibration.md",
        "STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step15_source_keywords_exist():
    source = "\n".join(read_text(path) for path in ["src/momentum_accounting.py", "src/calibration.py"])
    required_keywords = [
        "class MomentumAccounting3D",
        "hydro_force_sum",
        "cell_force_sum",
        "solid_particle_momentum",
        "moving_boundary_accounting_row",
        "classify_calibration_row",
        "choose_recommended_row",
        "write_calibration_summary",
        "reaction_scale",
        "force_cap_norm",
        "sign_reversed",
        "solid_slowdown",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source]
    assert missing == []


def test_step15_logs_record_success_markers():
    expected_markers = {
        "logs/step15_momentum_accounting.log": "[OK] Step 15 momentum accounting sanity finished",
        "logs/step15_reaction_scale_sweep_box_32.log": "[OK] Step 15 reaction scale sweep box 32 finished",
        "logs/step15_force_cap_sweep_box_48.log": "[OK] Step 15 force cap sweep box 48 finished",
        "logs/step15_squid_proxy_calibrated_window.log": "[OK] Step 15 squid proxy calibrated window finished",
        "logs/step15_calibrated_vs_original.log": "[OK] Step 15 calibrated vs original comparison finished",
        "logs/step15_artifact_manifest.log": "[OK] Step 15 artifact manifest finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_text(path):
            missing.append(f"{path}: {marker}")

    assert missing == []


def test_step15_accounting_timeseries_is_valid():
    rows = read_csv_rows("outputs/step15_momentum_accounting/accounting_timeseries.csv")
    assert rows

    for row in rows:
        assert_finite_row(row, excluded=("force_sign_consistent",))
        assert int(float(row["bb_link_count"])) > 0
        assert as_float(row, "cell_force_sum_x") == 0.0
        assert as_bool(row["force_sign_consistent"])
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0

    first = rows[0]
    assert as_float(first, "bb_net_fluid_impulse_x") > 0.0
    assert as_float(first, "bb_net_solid_force_x") < 0.0
    assert as_float(first, "hydro_force_sum_x") < 0.0
    assert as_float(first, "net_grid_reaction_force_x") < 0.0

    npz_path = ROOT / "outputs/step15_momentum_accounting/accounting_timeseries.npz"
    payload = np.load(npz_path, allow_pickle=False)
    assert "columns" in payload.files
    assert "bb_link_count" in payload.files


def test_step15_reaction_scale_sweep_is_valid():
    rows = read_csv_rows("outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.csv")
    assert {as_float(row, "reaction_scale") for row in rows} == {0.25, 0.5, 1.0, 2.0}

    expected_stable = {0.25, 0.5, 1.0}
    stable_expected_rows = [row for row in rows if as_float(row, "reaction_scale") in expected_stable]
    assert len(stable_expected_rows) == 3
    assert sum(1 for row in stable_expected_rows if as_bool(row["stable"])) >= 3

    for row in rows:
        assert_finite_row(
            row,
            excluded=("geometry_type", "stable", "well_behaved", "over_damped", "sign_reversed", "classification_reason"),
        )
        if as_bool(row["stable"]):
            assert as_float(row, "solid_slowdown") >= 0.0
    assert_stable_rows(rows)

    payload = np.load(ROOT / "outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.npz")
    assert "reaction_scale" in payload.files


def test_step15_force_cap_sweep_is_valid():
    rows = read_csv_rows("outputs/step15_force_cap_sweep_box_48/force_cap_sweep.csv")
    values = {round(as_float(row, "force_cap_norm"), 8) for row in rows}
    assert {0.00001, 0.000025, 0.00005, 0.0001}.issubset(values)

    known_good = [row for row in rows if math.isclose(as_float(row, "force_cap_norm"), 0.000025, rel_tol=0.0, abs_tol=1.0e-12)]
    assert len(known_good) == 1
    assert as_bool(known_good[0]["stable"])

    required_stable = [row for row in rows if round(as_float(row, "force_cap_norm"), 8) in {0.00001, 0.000025, 0.00005}]
    assert sum(1 for row in required_stable if as_bool(row["stable"])) >= 2

    for row in rows:
        assert_finite_row(
            row,
            excluded=("geometry_type", "stable", "well_behaved", "over_damped", "sign_reversed", "classification_reason"),
        )
    assert_stable_rows(rows)

    payload = np.load(ROOT / "outputs/step15_force_cap_sweep_box_48/force_cap_sweep.npz")
    assert "force_cap_norm" in payload.files


def test_step15_squid_proxy_calibration_is_valid():
    rows = read_csv_rows("outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.csv")
    assert len(rows) >= 3
    assert sum(1 for row in rows if as_bool(row["stable"])) >= 2

    for row in rows:
        assert row["geometry_type"] == "squid_proxy"
        assert_finite_row(
            row,
            excluded=("geometry_type", "stable", "well_behaved", "over_damped", "sign_reversed", "classification_reason"),
        )
    assert_stable_rows(rows)

    payload = np.load(ROOT / "outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.npz")
    assert "force_cap_norm" in payload.files


def test_step15_comparison_and_recommended_configs_are_valid():
    rows = read_csv_rows("outputs/step15_calibrated_vs_original/comparison.csv")
    by_label = {row["label"]: row for row in rows}
    assert {"original_step14", "recommended_step15"}.issubset(by_label)
    assert as_bool(by_label["recommended_step15"]["stable"])
    assert not as_bool(by_label["recommended_step15"]["sign_reversed"])
    assert "selected" in by_label["recommended_step15"]["recommendation"]

    for row in rows:
        assert_finite_row(row, excluded=("label", "stable", "well_behaved", "sign_reversed", "recommendation"))
    assert_stable_rows(rows)

    for path in ["configs/step15_mb_recommended_box_48.json", "configs/step15_mb_recommended_squid_proxy_48.json"]:
        config = read_json(path)
        assert config["coupling_mode"] == "moving_boundary"
        assert config["write_vtk"] is False
        assert config["write_particles"] is False

    payload = np.load(ROOT / "outputs/step15_calibrated_vs_original/comparison.npz")
    assert "labels" in payload.files


def test_step15_artifact_manifest_is_valid():
    summary = read_json("outputs/step15_artifact_manifest/artifact_summary.json")
    assert int(summary["file_count"]) > 0
    assert int(summary["total_size_bytes"]) > 0
    assert float(summary["total_size_mb"]) > 0.0
    assert int(summary["large_file_count"]) >= 0


def test_step15_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/10_performance_memory.md",
        "docs/13_larger_grid_validation.md",
        "docs/14_moving_boundary_calibration.md",
        "STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())

    required_scope = [
        "Step 15 does not change the moving bounce-back formula",
        "Step 15 does not add new FSI physics",
        "MomentumAccounting3D",
        "reaction_scale",
        "force_cap_norm",
        "The transfer remains an engineering coupling scale.",
        "Strict link-area momentum-conserving coupling is future work.",
        "squid_proxy is procedural and not real squid validation.",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_claims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "biomechanically accurate squid",
        "anatomically accurate squid",
        "strict momentum-conserving FSI is complete",
        "implements two_phase",
        "implements contact_angle",
        "implements ReducedSquidFSI",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined_docs]
    assert offenders == []

    production_text = combined_docs.replace("not production benchmark", "")
    production_text = production_text.replace("not a production benchmark", "")
    assert "production benchmark" not in production_text


def test_step15_report_acceptance_complete():
    report = read_text("STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 15 final commit",
        "- [x] src/momentum_accounting.py exists",
        "- [x] src/calibration.py exists",
        "- [x] src/__init__.py exports MomentumAccounting3D and calibration helpers if appropriate",
        "- [x] configs/step15_mb_calibration_box_32.json exists",
        "- [x] configs/step15_mb_force_cap_box_48.json exists",
        "- [x] configs/step15_mb_calibration_squid_proxy_48.json exists",
        "- [x] configs/step15_mb_recommended_box_48.json exists",
        "- [x] configs/step15_mb_recommended_squid_proxy_48.json exists",
        "- [x] accounting sanity baseline passes",
        "- [x] bb_link_count > 0 in accounting sanity",
        "- [x] bb_net_fluid_impulse_x > 0 for +x moving boundary",
        "- [x] bb_net_solid_force_x < 0",
        "- [x] hydro_force_sum_x < 0",
        "- [x] net_grid_reaction_force_x < 0",
        "- [x] cell_force_sum_x == 0",
        "- [x] force_sign_consistent is true for recommended rows",
        "- [x] reaction_scale sweep passes",
        "- [x] reaction_scale sweep includes 0.25, 0.5, 1.0, 2.0",
        "- [x] force_cap sweep 48^3 passes",
        "- [x] force_cap sweep includes 0.000025",
        "- [x] Step 14 known-good 0.000025 force cap remains stable",
        "- [x] squid_proxy calibrated window passes",
        "- [x] calibrated vs original comparison passes",
        "- [x] recommended box 48 config is stable",
        "- [x] recommended squid_proxy 48 config is stable",
        "- [x] no sign reversal in recommended configs unless explicitly documented as fallback",
        "- [x] rho_min > 0.95 for all stable rows",
        "- [x] rho_max < 1.05 for all stable rows",
        "- [x] lbm_max_v < 0.1 for all stable rows",
        "- [x] mpm_min_J > 0 for all stable rows",
        "- [x] mpm_max_speed < 10 for all stable rows",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no real squid validation claims",
        "- [x] no sparse storage implementation",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count controlled and reported",
        "- [x] docs/14_moving_boundary_calibration.md exists",
        "- [x] docs state engineering coupling scale and future strict momentum work",
        "- [x] README.md updated conservatively",
        "- [x] docs/08_roadmap.md updated",
        "- [x] docs/09_api_reference.md updated",
        "- [x] docs/13_larger_grid_validation.md updated",
        "- [x] STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md complete",
        "- [x] tests/test_step15_moving_boundary_calibration_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step15_pytest.log exists",
        "- [x] git diff --check passes",
        "- [x] Step 15 artifacts are committed",
        "- [x] Step 15 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
