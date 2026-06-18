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


def test_step13_required_artifacts_exist():
    required_paths = [
        "src/geometry_config.py",
        "src/geometry.py",
        "src/geometry_utils.py",
        "docs/12_geometry_ingestion.md",
        "configs/step13_box_geometry.json",
        "configs/step13_ellipsoid_geometry.json",
        "configs/step13_squid_proxy_geometry.json",
        "configs/step13_squid_proxy_none.json",
        "configs/step13_squid_proxy_penalty.json",
        "configs/step13_squid_proxy_moving_boundary.json",
        "baseline_tests/run_step13_geometry_sampler_box.py",
        "baseline_tests/run_step13_geometry_sampler_ellipsoid.py",
        "baseline_tests/run_step13_squid_proxy_geometry.py",
        "baseline_tests/run_step13_driver_squid_proxy_modes.py",
        "baseline_tests/run_step13_artifact_manifest.py",
        "logs/step13_geometry_box.log",
        "logs/step13_geometry_ellipsoid.log",
        "logs/step13_squid_proxy_geometry.log",
        "logs/step13_squid_proxy_modes.log",
        "logs/step13_artifact_manifest.log",
        "outputs/step13_geometry_box/particles_x.npy",
        "outputs/step13_geometry_ellipsoid/geometry_occupancy.npy",
        "outputs/step13_squid_proxy_geometry/particles_x.npy",
        "outputs/step13_squid_proxy_geometry/geometry_occupancy.npy",
        "outputs/step13_squid_proxy_modes/mode_results.csv",
        "outputs/step13_artifact_manifest/artifact_summary.json",
        "STEP13_GEOMETRY_INGESTION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step13_source_contract_keywords():
    source_paths = [
        "src/geometry_config.py",
        "src/geometry.py",
        "src/geometry_utils.py",
        "src/mpm_solid.py",
        "src/fsi_config.py",
        "src/fsi_driver.py",
        "baseline_tests/run_step13_geometry_sampler_box.py",
        "baseline_tests/run_step13_geometry_sampler_ellipsoid.py",
        "baseline_tests/run_step13_squid_proxy_geometry.py",
        "baseline_tests/run_step13_driver_squid_proxy_modes.py",
        "baseline_tests/run_step13_artifact_manifest.py",
    ]
    combined = "\n".join(read_text(path) for path in source_paths if (ROOT / path).is_file())

    required_keywords = [
        "class GeometryConfig",
        "class GeometrySampler3D",
        "geometry_type",
        "sample_particles",
        "voxelize",
        "squid_proxy",
        "ellipsoid",
        "init_from_numpy",
        "FSIDriver3D",
        "MPMSolid3D",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in combined]
    assert missing == []

    forbidden_claims = ["implements two_phase", "implements contact_angle", "ReducedSquidFSI"]
    offenders = [claim for claim in forbidden_claims if claim in combined]
    assert offenders == []


def test_step13_logs_record_success_markers():
    expected_markers = {
        "logs/step13_geometry_box.log": "[OK] Step 13 box geometry sampler finished",
        "logs/step13_geometry_ellipsoid.log": "[OK] Step 13 ellipsoid geometry sampler finished",
        "logs/step13_squid_proxy_geometry.log": "[OK] Step 13 squid proxy geometry finished",
        "logs/step13_squid_proxy_modes.log": "[OK] Step 13 squid proxy driver modes finished",
        "logs/step13_artifact_manifest.log": "[OK] Step 13 artifact manifest finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_text(path):
            missing.append(f"{path}: {marker}")

    assert missing == []


def test_step13_particle_and_voxel_outputs_are_valid():
    particle_paths = [
        "outputs/step13_geometry_box/particles_x.npy",
        "outputs/step13_squid_proxy_geometry/particles_x.npy",
    ]
    for path in particle_paths:
        particles = np.load(ROOT / path)
        assert particles.shape == (4096, 3)
        assert np.all(np.isfinite(particles))
        assert np.min(particles) >= 0.0
        assert np.max(particles) <= 1.0

    occupancy_paths = [
        "outputs/step13_geometry_ellipsoid/geometry_occupancy.npy",
        "outputs/step13_squid_proxy_geometry/geometry_occupancy.npy",
    ]
    for path in occupancy_paths:
        occupancy = np.load(ROOT / path)
        assert occupancy.shape == (32, 32, 32)
        assert np.all(np.isfinite(occupancy))
        assert int(np.count_nonzero(occupancy)) > 0


def test_step13_geometry_stats_are_valid():
    stats_paths = [
        "outputs/step13_geometry_box/geometry_stats.json",
        "outputs/step13_geometry_ellipsoid/geometry_stats.json",
        "outputs/step13_squid_proxy_geometry/geometry_stats.json",
    ]

    for path in stats_paths:
        stats = json.loads((ROOT / path).read_text(encoding="utf-8"))
        assert int(stats["particle_count"]) == 4096
        assert int(stats["active_cell_count"]) > 0
        assert float(stats["projected_mass"]) > 0.0
        assert float(stats["geometry_volume"]) > 0.0
        assert math.isfinite(float(stats["geometry_volume"]))

    squid_stats = json.loads((ROOT / "outputs/step13_squid_proxy_geometry/geometry_stats.json").read_text(encoding="utf-8"))
    assert squid_stats["geometry_type"] == "squid_proxy"
    assert int(squid_stats["occupied_count"]) > 0
    assert "not anatomical or validated squid geometry" in squid_stats["scope_note"]


def test_step13_squid_proxy_modes_are_valid():
    rows = read_csv_rows("outputs/step13_squid_proxy_modes/mode_results.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty", "moving_boundary"}

    for row in rows:
        assert row["stable"] == "True"
        assert float(row["rho_min"]) > 0.95
        assert float(row["rho_max"]) < 1.05
        assert float(row["lbm_max_v"]) < 0.1
        assert float(row["mpm_min_J"]) > 0.0
        assert float(row["mpm_max_speed"]) < 10.0
        assert int(float(row["active_cell_count"])) > 0
        assert float(row["projected_mass"]) > 0.0

    assert float(by_mode["penalty"]["cell_force_max_norm"]) > 0.0
    assert float(by_mode["moving_boundary"]["cell_force_max_norm"]) == 0.0
    assert int(float(by_mode["moving_boundary"]["bb_link_count"])) > 0
    moving_response = float(by_mode["moving_boundary"]["hydro_force_max_norm"])
    penalty_response = float(by_mode["penalty"]["cell_force_max_norm"])
    assert moving_response > 0.0
    assert penalty_response > 0.0


def test_step13_artifact_summary_is_valid():
    summary = json.loads((ROOT / "outputs/step13_artifact_manifest/artifact_summary.json").read_text(encoding="utf-8"))

    assert int(summary["file_count"]) > 0
    assert int(summary["total_size_bytes"]) > 0
    assert float(summary["total_size_mb"]) > 0.0
    assert int(summary["large_file_count"]) >= 0
    assert isinstance(summary["by_extension"], dict)


def test_step13_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/11_artifact_policy.md",
        "docs/12_geometry_ingestion.md",
        "STEP13_GEOMETRY_INGESTION_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())

    required_scope = [
        "GeometryConfig",
        "GeometrySampler3D",
        "box",
        "ellipsoid",
        "squid_proxy",
        "procedural",
        "not real squid validation",
        "Step 13 does not add new FSI physics",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_overclaims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "biomechanically accurate squid",
        "anatomically accurate squid",
        "production-grade geometry pipeline",
        "strict momentum-conserving FSI is complete",
    ]
    offenders = [claim for claim in forbidden_overclaims if claim in combined_docs]
    assert offenders == []


def test_step13_report_acceptance_complete():
    report = read_text("STEP13_GEOMETRY_INGESTION_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 13 final commit",
        "- [x] src/geometry_config.py exists",
        "- [x] src/geometry.py exists",
        "- [x] src/geometry_utils.py exists",
        "- [x] src/__init__.py exports GeometryConfig and GeometrySampler3D",
        "- [x] MPMSolid3D supports init_from_numpy or init_from_particle_cloud",
        "- [x] FSIDriverConfig supports geometry_type",
        "- [x] FSIDriver3D can initialize non-box geometry through geometry_type",
        "- [x] geometry_type=\"box\" preserves existing box/default behavior",
        "- [x] configs/step13_box_geometry.json exists",
        "- [x] configs/step13_ellipsoid_geometry.json exists",
        "- [x] configs/step13_squid_proxy_geometry.json exists",
        "- [x] configs/step13_squid_proxy_none.json exists",
        "- [x] configs/step13_squid_proxy_penalty.json exists",
        "- [x] configs/step13_squid_proxy_moving_boundary.json exists",
        "- [x] box geometry sampler baseline passes",
        "- [x] ellipsoid geometry sampler baseline passes",
        "- [x] squid proxy geometry baseline passes",
        "- [x] squid proxy driver modes baseline passes",
        "- [x] Step 13 artifact manifest baseline passes",
        "- [x] none / penalty / moving_boundary run on squid_proxy geometry",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] mpm_max_speed < 10",
        "- [x] particle positions are finite",
        "- [x] geometry occupancy is finite",
        "- [x] active_cell_count > 0",
        "- [x] projected_mass > 0",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] docs explicitly say squid_proxy is not real squid validation",
        "- [x] report explicitly says squid_proxy is not real squid validation",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no sparse storage implementation",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact manifest reports total size and large_file_count",
        "- [x] README.md documents geometry support",
        "- [x] docs/08_roadmap.md updated",
        "- [x] docs/09_api_reference.md updated",
        "- [x] docs/11_artifact_policy.md updated",
        "- [x] STEP13_GEOMETRY_INGESTION_REPORT.md complete",
        "- [x] tests/test_step13_geometry_ingestion_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step13_pytest.log exists",
        "- [x] git diff --check passes",
        "- [x] Step 13 artifacts are committed",
        "- [x] Step 13 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
