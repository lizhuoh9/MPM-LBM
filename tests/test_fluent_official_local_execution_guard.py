import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SCHEMA = ROOT / "configs" / "fluent_official_2way_fsi_local_execution_schema.json"
MONITOR_SCHEMA = ROOT / "configs" / "fluent_official_monitor_export_schema.json"
GUARD_DOC = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "fluent_official_local_execution_guard.md"
GUARD_REPORT = ROOT / "outputs" / "fluent_official_local_execution_prep" / "guard_report.json"

PRIVATE_ROOT = "benchmarks/private/fluent_fsi_2way/"
OFFICIAL_LOCAL_ONLY_FILES = {
    "fsi_2way.zip",
    "flap.msh",
    "steady_fluid_flow.jou",
}


def test_fluent_official_local_execution_guard_doc_is_prep_only():
    text = _single_spaced(GUARD_DOC.read_text(encoding="utf-8"))

    for phrase in [
        "No Fluent run is executed by this guard.",
        "Official payloads remain local under benchmarks/private/fluent_fsi_2way/.",
        "This guard does not permit validation claims.",
        "Comparison output is gap-only until a later explicit validation step passes.",
    ]:
        assert phrase in text


def test_fluent_official_local_execution_schema_is_local_only():
    schema = _read_json(EXECUTION_SCHEMA)

    assert schema["title"] == "Fluent official two-way FSI local execution manifest"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["local_private_root"]["const"] == PRIVATE_ROOT
    assert schema["properties"]["execution_scope"]["const"] == "manual_local_only"
    assert schema["properties"]["commit_official_payloads"]["const"] is False
    assert schema["properties"]["validation_claim_allowed"]["const"] is False
    for key in [
        "fluent_executable",
        "local_private_root",
        "archive_path",
        "mesh_path",
        "journal_path",
        "case_output_dir",
        "monitor_export_path",
        "execution_scope",
        "commit_official_payloads",
        "validation_claim_allowed",
    ]:
        assert key in schema["required"]


def test_fluent_official_monitor_export_schema_is_gap_only():
    schema = _read_json(MONITOR_SCHEMA)

    assert schema["title"] == "Fluent official monitor export schema"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["source"]["const"] == "official_fluent_manual_export"
    assert schema["properties"]["comparison_scope"]["const"] == "gap_only"
    assert schema["properties"]["validation_claim_allowed"]["const"] is False
    assert schema["required"] == [
        "source",
        "comparison_scope",
        "validation_claim_allowed",
        "columns",
        "units",
    ]
    assert "time_s" in schema["properties"]["columns"]["items"]["enum"]
    assert "flap_tip_total_displacement_m" in schema["properties"]["columns"]["items"]["enum"]


def test_fluent_official_local_execution_guard_report_blocks_external_action():
    report = _read_json(GUARD_REPORT)

    assert report["status"] == "prep_only_pass"
    assert report["fluent_run_executed"] is False
    assert report["external_action_taken"] is False
    assert report["official_payload_committed"] is False
    assert report["validation_claim_allowed"] is False
    assert report["gap_only_comparison_readiness"] is True
    assert report["local_private_root"] == PRIVATE_ROOT
    assert set(report["required_local_only_files"]) == OFFICIAL_LOCAL_ONLY_FILES
    assert report["execution_schema"] == "configs/fluent_official_2way_fsi_local_execution_schema.json"
    assert report["monitor_export_schema"] == "configs/fluent_official_monitor_export_schema.json"


def test_fluent_official_payloads_are_not_tracked():
    tracked = _tracked_files()
    forbidden = [
        path
        for path in tracked
        if path.startswith(PRIVATE_ROOT)
        or path.endswith("fsi_2way.zip")
        or path.endswith("flap.msh")
        or path.endswith("steady_fluid_flow.jou")
        or path.endswith(".cas.h5")
        or path.endswith(".dat.h5")
        or path.endswith(".wbpj")
    ]

    assert forbidden == []


def _read_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def _single_spaced(text: str) -> str:
    return " ".join(text.split())
