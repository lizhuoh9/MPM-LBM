import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CAMPAIGN_BASE_COMMIT = "516b1aaa4c71d5468ce5ea444a21ffa07741c8bc"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _assert_ancestor(ancestor: str, descendant: str) -> None:
    subprocess.check_call(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT)


def _fresh_tmp_dir(name: str) -> Path:
    path = ROOT / "outputs" / "tmp" / "step125_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_step125_current_campaign_records_split_commit_identity():
    active_path = ROOT / "docs" / "current" / "ACTIVE_CAMPAIGN.json"
    gate_report_path = ROOT / "outputs" / "step121_lbm_boundary_real_campaign_and_gate_correction" / "step121_gate_report.json"
    manifest_path = ROOT / "outputs" / "step121_lbm_boundary_real_campaign_and_gate_correction" / "campaign_manifest.json"

    active = json.loads(active_path.read_text(encoding="utf-8"))
    gate = json.loads(gate_report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    head = _git("rev-parse", "HEAD")

    assert active["campaign_base_commit"] == CAMPAIGN_BASE_COMMIT
    assert active["base_commit"] == active["campaign_base_commit"]
    assert active["current_code_commit"]
    assert active["current_code_commit"] != active["campaign_base_commit"]
    _assert_ancestor(active["campaign_base_commit"], active["current_code_commit"])
    _assert_ancestor(active["current_code_commit"], head)
    assert active["state"] == gate["campaign_state"]
    assert active["final_classification"] == gate["final_classification"]
    assert manifest["campaign_base_commit"] == active["campaign_base_commit"]
    assert manifest["current_code_commit"] == active["current_code_commit"]
    assert manifest["git_commit"] == manifest["current_code_commit"]
    assert manifest["phase_commit_history"]


def test_step125_manifest_records_phase_commit_history():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        STEP121_CAMPAIGN_MANIFEST_SCHEMA_VERSION,
        step121_reference_48_specs,
        step121_smoke_specs,
        write_step121_campaign_manifest,
    )

    head = _git("rev-parse", "HEAD")

    out = _fresh_tmp_dir("manifest_history")
    smoke = write_step121_campaign_manifest(
        out,
        step121_smoke_specs(),
        phase="smoke",
        campaign_base_commit=CAMPAIGN_BASE_COMMIT,
    )

    assert STEP121_CAMPAIGN_MANIFEST_SCHEMA_VERSION >= 2
    assert smoke["campaign_base_commit"] == CAMPAIGN_BASE_COMMIT
    assert smoke["current_code_commit"] == head
    assert smoke["git_commit"] == smoke["current_code_commit"]
    assert smoke["phase_history"] == ["smoke"]
    assert smoke["phase_commit_history"] == [{"phase": "smoke", "code_commit": head}]
    smoke_rows = set(smoke["expected_rows"])

    references = write_step121_campaign_manifest(
        out,
        step121_reference_48_specs(output_interval=25),
        phase="references48",
        campaign_base_commit=CAMPAIGN_BASE_COMMIT,
    )

    assert smoke_rows.issubset(set(references["expected_rows"]))
    assert "references48" in references["phase_history"]
    assert {"phase": "references48", "code_commit": head} in references["phase_commit_history"]
    assert references["current_code_commit"] == head
    assert references["git_commit"] == head


def test_step125_step120_rows_record_code_commit_at_run():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        _tau_feasibility_report,
        _write_nonstepped_row,
    )

    head = _git("rev-parse", "HEAD")
    spec = Step120RunSpec(
        name="step125_nonstepped_provenance_row",
        nx=4,
        ny=3,
        nz=3,
        n_steps=2,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=2,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )

    out = _fresh_tmp_dir("step120_row")
    _write_nonstepped_row(
        spec,
        out / spec.name,
        _tau_feasibility_report(spec),
        "step125_test_skip",
    )
    finite = json.loads((out / spec.name / "finite_stability_report.json").read_text(encoding="utf-8"))
    metadata = json.loads((out / spec.name / "run_metadata.json").read_text(encoding="utf-8"))

    assert finite["summary_row"]["code_commit_at_run"] == head
    assert metadata["code_commit_at_run"] == head
