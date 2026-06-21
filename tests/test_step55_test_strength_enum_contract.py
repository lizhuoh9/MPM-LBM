import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DURABLE_PYTEST_INTERPRETATION = (
    "A passing full pytest run means contract/artifact/proxy/solver-smoke tests passed "
    "according to the test strength audit classification."
)


def test_step55_test_strength_enum_audit_passes():
    payload = read_json("outputs/step55_test_strength_enum_audit/test_strength_enum_audit.json")
    summary = payload["summary"]
    assert summary["test_strength_enum_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["allowed_count"])
    assert int(summary["out_of_policy_count"]) == 0
    assert summary["pytest_result_interpretation"] == DURABLE_PYTEST_INTERPRETATION
    assert all(row["allowed"] is True for row in payload["rows"])


def test_step54_test_strength_output_matches_step55_policy():
    policy = read_json("configs/step55_test_strength_enum_policy.json")
    allowed = set(policy["allowed_test_strength_levels"])
    payload = read_json("outputs/step54_test_strength_audit/test_strength_audit.json")
    assert payload["summary"]["test_strength_audit_pass"] is True
    assert payload["summary"]["test_suite_result_interpretation"] == DURABLE_PYTEST_INTERPRETATION
    assert int(payload["summary"]["out_of_policy_strength_level_count"]) == 0
    assert {row["test_strength_level"] for row in payload["rows"]}.issubset(allowed)


def test_step55_step54_regression_guard_passes():
    payload = read_json("outputs/step55_step54_regression_guard/step54_regression_guard.json")
    summary = payload["summary"]
    assert summary["step54_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step55_artifact_manifest_passes_and_protected_dirs_are_clean():
    summary = read_json("outputs/step55_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert float(summary["step55_total_size_mb"]) < 5.0
    assert int(summary["large_file_count"]) == 0
    assert int(summary["step55_vtr_count"]) == 0
    assert int(summary["step55_particle_npy_count"]) == 0
    assert int(summary["protected_external_taichi_lbm3d_step55_file_count"]) == 0
    assert int(summary["protected_real_geometry_candidates_step55_file_count"]) == 0


def test_step54_long_lived_surfaces_do_not_use_stale_pytest_count():
    for path in [
        "STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md",
        "configs/step54_evidence_classification_policy.json",
        "tests/test_step54_repository_evidence_integrity_repair_contract.py",
        "outputs/step54_test_strength_audit/test_strength_audit.json",
        "outputs/step54_test_strength_audit/test_strength_audit_summary.csv",
    ]:
        text = read_text(path)
        assert "604/614" not in text
        assert "624 passed" not in text
    assert DURABLE_PYTEST_INTERPRETATION in read_text("STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md")


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
