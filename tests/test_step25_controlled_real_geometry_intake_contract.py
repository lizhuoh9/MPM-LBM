import csv
import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP25_REQUIRED_FILES = [
    "STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_GOAL.md",
    "STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md",
    "src/geometry_fingerprint.py",
    "src/geometry_candidate_manifest.py",
    "src/geometry_normalization.py",
    "src/geometry_intake.py",
    "configs/step25_candidate_smoke_mesh_descriptor.json",
    "configs/step25_candidate_smoke_voxel_descriptor.json",
    "configs/step25_intake_policy.json",
    "data/real_geometry_candidates/README.md",
    "data/real_geometry_candidates/.gitkeep",
    "baseline_tests/step25_common.py",
    "baseline_tests/run_step25_candidate_manifest.py",
    "baseline_tests/run_step25_real_geometry_intake_smoke.py",
    "baseline_tests/run_step25_mesh_candidate_quality.py",
    "baseline_tests/run_step25_voxel_candidate_quality.py",
    "baseline_tests/run_step25_normalization_reports.py",
    "baseline_tests/run_step25_sampling_reproducibility.py",
    "baseline_tests/run_step25_projection_smoke.py",
    "baseline_tests/run_step25_step24_regression_guard.py",
    "baseline_tests/run_step25_artifact_manifest.py",
    "docs/24_controlled_real_geometry_intake.md",
    "docs/25_real_geometry_candidate_policy.md",
    "tests/test_step25_controlled_real_geometry_intake_contract.py",
]

STEP25_DESCRIPTORS = [
    "configs/step25_candidate_smoke_mesh_descriptor.json",
    "configs/step25_candidate_smoke_voxel_descriptor.json",
]

STEP25_LOG_MARKERS = {
    "logs/step25_candidate_manifest.log": "[OK] Step 25 candidate manifest finished",
    "logs/step25_real_geometry_intake_smoke.log": "[OK] Step 25 real geometry intake smoke finished",
    "logs/step25_mesh_candidate_quality.log": "[OK] Step 25 mesh candidate quality finished",
    "logs/step25_voxel_candidate_quality.log": "[OK] Step 25 voxel candidate quality finished",
    "logs/step25_normalization_reports.log": "[OK] Step 25 normalization reports finished",
    "logs/step25_sampling_reproducibility.log": "[OK] Step 25 sampling reproducibility finished",
    "logs/step25_projection_smoke.log": "[OK] Step 25 projection smoke finished",
    "logs/step25_step24_regression_guard.log": "[OK] Step 25 Step 24 regression guard finished",
    "logs/step25_artifact_manifest.log": "[OK] Step 25 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 25 is controlled real geometry intake, not real squid validation.",
    "Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.",
    "Step 25 does not implement squid swimming.",
    "Step 25 does not implement squid actuation.",
    "Step 25 does not implement new FSI physics.",
    "Step 25 does not validate production sharp-interface FSI.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
    "The moving bounce-back formula is unchanged.",
    "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
    "Candidate intake does not perform production mesh repair or automatic remeshing.",
    "Raw large real geometry files and scan data are not committed.",
]

FORBIDDEN_CLAIMS = [
    "real squid simulation is validated",
    "validated squid swimming",
    "production mesh repair is complete",
    "automatic remeshing is implemented",
    "production-ready mesh import",
    "production-ready sharp-interface FSI",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
    "validated squid actuation",
    "final solver readiness",
]


def test_step25_required_artifacts_exist():
    missing = [path for path in STEP25_REQUIRED_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step25_candidate_descriptors_are_valid():
    descriptors = [read_json(path) for path in STEP25_DESCRIPTORS]
    ids = [descriptor["candidate_id"] for descriptor in descriptors]
    assert len(ids) == len(set(ids))
    for descriptor in descriptors:
        assert descriptor["geometry_type"] in {"mesh", "voxel"}
        assert descriptor["validation_scope"] == "intake_qa_normalization_sampling_projection_only"
        assert descriptor["quality_check_enabled"] is True
        assert descriptor["quality_check_strict"] is True
        assert descriptor["commit_policy"] in {
            "small_controlled_fixture_allowed",
            "do_not_commit_large_raw_geometry",
            "local_candidate_only",
        }
        assert int(descriptor["n_particles"]) > 0
        assert 0.0 <= float(descriptor["padding"]) < 0.5
        assert not descriptor["source_file"].replace("\\", "/").startswith("external/taichi_LBM3D")
        assert (ROOT / descriptor["source_file"]).is_file()


def test_step25_real_geometry_candidate_policy_is_documented():
    text = "\n".join(
        read_text(path)
        for path in [
            "data/real_geometry_candidates/README.md",
            "docs/24_controlled_real_geometry_intake.md",
            "docs/25_real_geometry_candidate_policy.md",
            ".gitignore",
        ]
    )
    policy_text = text.lower()
    for phrase in [
        "data/real_geometry_candidates/*",
        "!data/real_geometry_candidates/README.md",
        "!data/real_geometry_candidates/.gitkeep",
        "!data/real_geometry_candidates/*_descriptor.json",
        "do not commit large raw real geometry files",
        "do not commit scan data",
    ]:
        assert phrase.lower() in policy_text


def test_step25_candidate_manifest_is_valid():
    manifest = read_json("outputs/step25_candidate_manifest/candidate_manifest.json")
    rows = manifest["rows"]
    assert int(manifest["row_count"]) == 2
    assert len(read_csv_rows("outputs/step25_candidate_manifest/candidate_manifest.csv")) == 2
    ids = [row["candidate_id"] for row in rows]
    assert len(ids) == len(set(ids))
    for row in rows:
        assert row["manifest_pass"] is True
        assert row["geometry_type"] in {"mesh", "voxel"}
        assert row["validation_scope"] == "intake_qa_normalization_sampling_projection_only"
        assert row["quality_check_enabled"] is True
        assert row["quality_check_strict"] is True
        assert int(row["size_bytes"]) > 0
        assert len(row["sha256"]) == 64
        assert not bool(row["is_large"])
        assert ":" not in row["source_file_redacted"]
        assert "\\Users\\" not in row["source_file_redacted"]


def test_step25_mesh_quality_report_is_valid():
    rows = read_json("outputs/step25_mesh_candidate_quality/mesh_candidate_quality.json")["rows"]
    assert len(rows) == 1
    row = rows[0]
    assert row["geometry_type"] == "mesh"
    assert row["quality_pass"] is True
    assert row["quality_severity"] == "ok"
    assert int(row["vertices_count"]) > 0
    assert int(row["faces_count"]) > 0
    assert row["has_valid_face_indices"] is True
    assert int(row["degenerate_face_count"]) == 0
    assert int(row["boundary_edge_count"]) == 0
    assert int(row["nonmanifold_edge_count"]) == 0
    assert (ROOT / row["quality_report_path"]).is_file()


def test_step25_voxel_quality_report_is_valid():
    rows = read_json("outputs/step25_voxel_candidate_quality/voxel_candidate_quality.json")["rows"]
    assert len(rows) == 1
    row = rows[0]
    assert row["geometry_type"] == "voxel"
    assert row["quality_pass"] is True
    assert row["quality_severity"] == "ok"
    assert int(row["occupied_count"]) > 0
    assert int(row["connected_component_count"]) >= 1
    assert math.isfinite(float(row["largest_component_fraction"]))
    assert (ROOT / row["quality_report_path"]).is_file()


def test_step25_normalization_report_is_valid():
    summary = read_json("outputs/step25_normalization_reports/normalization_summary.json")
    assert int(summary["row_count"]) == 2
    for row in summary["rows"]:
        report = read_json(row["normalization_report_path"])
        assert report["normalized_inside_domain"] is True
        assert math.isfinite(float(report["scale_factor"]))
        assert all(math.isfinite(float(value)) for value in report["translation"])
        assert report["source_file_modified"] is False
        assert report["repair_performed"] is False
        assert report["remeshing_performed"] is False
        assert all(0.0 <= float(value) <= 1.0 for value in report["normalized_bounds_min"])
        assert all(0.0 <= float(value) <= 1.0 for value in report["normalized_bounds_max"])


def test_step25_sampling_reproducibility_is_valid():
    summary = read_json("outputs/step25_sampling_reproducibility/sampling_reproducibility.json")
    assert int(summary["row_count"]) == 2
    for row in summary["rows"]:
        assert row["reproducibility_pass"] is True
        assert int(row["particle_count_first"]) == int(row["particle_count_second"])
        assert float(row["geometry_volume_first"]) == float(row["geometry_volume_second"])
        assert float(row["mass_sum_first"]) == float(row["mass_sum_second"])
        assert row["sampled_position_hash_first"] == row["sampled_position_hash_second"]
        assert row["vol0_hash_first"] == row["vol0_hash_second"]
        assert row["mass_hash_first"] == row["mass_hash_second"]
        assert math.isfinite(float(row["relative_mass_error"]))


def test_step25_projection_smoke_is_valid():
    summary = read_json("outputs/step25_projection_smoke/projection_smoke_results.json")
    assert int(summary["row_count"]) == 2
    for row in summary["rows"]:
        assert row["projection_pass"] is True
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert float(row["solid_phi_min"]) >= 0.0
        assert float(row["solid_phi_max"]) <= 1.0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert "projection-only" in row["scope_note"]


def test_step25_step24_regression_guard_is_valid():
    summary = read_json("outputs/step25_step24_regression_guard/step24_regression_guard.json")
    rows = read_csv_rows("outputs/step25_step24_regression_guard/step24_regression_guard.csv")
    assert int(summary["row_count"]) == 6
    assert int(summary["pass_count"]) == 6
    assert int(summary["quality_report_count"]) == 9
    assert int(summary["large_file_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step25_no_solver_or_coupler_formula_changes_claimed():
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/08_roadmap.md",
            "docs/09_api_reference.md",
            "docs/11_artifact_policy.md",
            "docs/12_geometry_ingestion.md",
            "docs/19_geometry_import_pipeline.md",
            "docs/21_geometry_quality_checks.md",
            "docs/22_quality_gated_imported_geometry_validation.md",
            "docs/23_strict_quality_gated_imported_geometry_long_run.md",
            "docs/24_controlled_real_geometry_intake.md",
            "docs/25_real_geometry_candidate_policy.md",
            "STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []

    geometry_config = read_text("src/geometry_config.py")
    fsi_config = read_text("src/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config


def test_step25_artifact_budget_is_valid():
    summary = read_json("outputs/step25_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step25_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 160.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["step25_vtr_count"]) == 0
    assert int(summary["step25_particle_npy_count"]) == 0
    assert int(summary["step25_descriptor_count"]) >= 2
    assert int(summary["step25_policy_doc_count"]) >= 2
    manifest_rows = read_csv_rows("outputs/step25_artifact_manifest/artifact_manifest.csv")
    step25_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step25")]
    assert not [path for path in step25_paths if path.endswith(".vtr")]
    assert not [path for path in step25_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step25_report_acceptance_complete():
    report = read_text("STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Candidate Manifest",
        "## 5. Intake Smoke",
        "## 6. Mesh Candidate Quality",
        "## 7. Voxel Candidate Quality",
        "## 8. Normalization Reports",
        "## 9. Sampling Reproducibility",
        "## 10. Projection Smoke",
        "## 11. Step 24 Regression Guard",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 26",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] candidate manifest generation passes",
        "- [x] candidate descriptors are valid",
        "- [x] raw candidate geometry commit policy is enforced",
        "- [x] mesh candidate strict quality report passes",
        "- [x] voxel candidate strict quality report passes",
        "- [x] normalization reports are finite and domain-bounded",
        "- [x] deterministic sampling reproducibility passes",
        "- [x] projection smoke passes",
        "- [x] Step 24 regression guard passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step25_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Step 25 contract test passes",
        "- [x] git diff --check passes",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step25_pytest.log").is_file()
    for path, marker in STEP25_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path

    external_status = subprocess.run(
        ["git", "status", "--short", "external/taichi_LBM3D"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert external_status.stdout.strip() == ""


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path: str) -> list[dict]:
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
