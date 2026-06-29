from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional


STEP = 142
SOURCE_STEP = 141
EXPECTED_STEP141_DECISION = "density_feedback_isolation_insufficient"
DEFAULT_STEP141_DECISION = Path("outputs") / "step141_density_feedback_isolation" / "step141_decision_summary.json"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step142_mass_neutral_plane_flux_design"
REPORT_JSON = "step142_design_readiness_report.json"
REPORT_MD = "step142_design_readiness_report.md"


def run_step142_mass_neutral_design_report(
    step141_decision: Path | str = DEFAULT_STEP141_DECISION,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Dict[str, Any]:
    del force
    decision_path = Path(step141_decision)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not decision_path.is_file():
        summary = _base_summary(
            status="missing_input",
            step141_decision=decision_path,
            source_hash=None,
            decision=None,
        )
        summary["missing_input"] = True
        summary["missing_input_path"] = _display_path(decision_path)
        return _write_report(out, summary)

    decision = _read_json(decision_path)
    decision_hash = sha256(decision_path.read_bytes()).hexdigest()
    source_case = decision.get("decision_case")
    if source_case != EXPECTED_STEP141_DECISION:
        summary = _base_summary(
            status="blocked_by_step141_decision",
            step141_decision=decision_path,
            source_hash=decision_hash,
            decision=decision,
        )
        summary["blocking_reason"] = (
            "Step142 design proposal requires Step141 decision_case "
            f"{EXPECTED_STEP141_DECISION!r}; observed {source_case!r}."
        )
        return _write_report(out, summary)

    summary = _base_summary(
        status="design_ready",
        step141_decision=decision_path,
        source_hash=decision_hash,
        decision=decision,
    )
    summary.update(
        {
            "missing_input": False,
            "step142_design_only": True,
            "step142_real_48_run_executed": False,
            "step142_real_48_row_count": 0,
            "step142_500step_run_executed": False,
            "step142_single_500step_final_evidence_proposal_allowed": False,
            "selected96_execution_allowed": False,
            "selected_static_execution_allowed": False,
            "validation_claim_allowed": False,
            "fluent_validation_claim_allowed": False,
            "fsi_validation_claim_allowed": False,
            "quasi2d_validation_claim_allowed": False,
            "production_readiness_claim_allowed": False,
            "step143_250step_diagnostic_proposal_allowed": True,
            "recommended_next_step": 143,
            "recommended_next_phase_name": "planeflux_mass_neutral_design48",
            "recommended_next_phase_scope": (
                "future bounded 48^3 / 250-step diagnostic only; not selected96, not Fluent, not FSI"
            ),
            "recommended_design": _recommended_design(),
            "report_only_fallback_design": _fallback_design(),
        }
    )
    return _write_report(out, summary)


def _base_summary(
    *,
    status: str,
    step141_decision: Path,
    source_hash: Optional[str],
    decision: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision = dict(decision or {})
    return {
        "artifact": "step142_design_readiness_report",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": status,
        "step141_decision_path": _display_path(step141_decision),
        "source_step141_decision_hash": source_hash,
        "source_step141_status": decision.get("status"),
        "source_step141_decision_case": decision.get("decision_case"),
        "source_step141_best_gain_rho": decision.get("best_gain_rho"),
        "source_step141_best_row_name": decision.get("best_row_name"),
        "source_step141_row_count": decision.get("row_count"),
        "source_step141_selected96_execution_allowed": decision.get("selected96_execution_allowed"),
        "source_step141_validation_claim_allowed": decision.get("validation_claim_allowed"),
        "source_step141_500step_proposal_allowed": decision.get(
            "step142_single_500step_final_evidence_proposal_allowed"
        ),
        "step142_design_only": True,
        "step142_real_48_run_executed": False,
        "step142_500step_run_executed": False,
        "step142_single_500step_final_evidence_proposal_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "step143_250step_diagnostic_proposal_allowed": False,
    }


def _recommended_design() -> Dict[str, Any]:
    return {
        "primary_mode": "global_mass_error_density_offset",
        "default_enabled": False,
        "runtime_active_in_step142": False,
        "reference_mass_mode": "initial",
        "planned_formula": (
            "mass_error = (mass_total - mass_initial) / mass_initial; "
            "rho_mass_feedback = clamp(-gain_mass * mass_error, -cap_mass, cap_mass); "
            "target_rho = outlet_rho + rho_mass_feedback + existing_rho_feedback"
        ),
        "config_fields": [
            "open_boundary_mass_neutral_flux_control_enabled",
            "open_boundary_mass_neutral_flux_control_mode",
            "open_boundary_mass_neutral_mass_error_gain",
            "open_boundary_mass_neutral_mass_error_cap",
            "open_boundary_mass_neutral_correction_blend",
            "open_boundary_mass_neutral_reference_mass_mode",
        ],
    }


def _fallback_design() -> Dict[str, Any]:
    return {
        "mode": "outlet_population_projection_report_only",
        "default_enabled": False,
        "runtime_active_in_step142": False,
        "purpose": (
            "Expose planned outlet-population projection telemetry without changing populations in Step142."
        ),
    }


def _write_report(out: Path, summary: Dict[str, Any]) -> Dict[str, Any]:
    _write_json(out / REPORT_JSON, summary)
    (out / REPORT_MD).write_text(_markdown(summary), encoding="utf-8")
    return summary


def _markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Step142 Mass-Neutral Plane-Flux Design Readiness",
        "",
        f"Status: `{summary['status']}`.",
        "",
        "This is a design-readiness artifact. no real Step142 48^3 row was run.",
        "",
        "Execution claims:",
        "",
        f"- `step142_real_48_run_executed = {str(summary['step142_real_48_run_executed']).lower()}`",
        f"- `step142_500step_run_executed = {str(summary['step142_500step_run_executed']).lower()}`",
        (
            "- `step142_single_500step_final_evidence_proposal_allowed = "
            f"{str(summary['step142_single_500step_final_evidence_proposal_allowed']).lower()}`"
        ),
        f"- `selected96_execution_allowed = {str(summary['selected96_execution_allowed']).lower()}`",
        f"- `validation_claim_allowed = {str(summary['validation_claim_allowed']).lower()}`",
        "",
    ]
    if summary["status"] == "design_ready":
        lines.extend(
            [
                "Recommended next step:",
                "",
                f"- Step: `{summary['recommended_next_step']}`",
                f"- Phase name proposal: `{summary['recommended_next_phase_name']}`",
                f"- Scope: {summary['recommended_next_phase_scope']}",
                "",
                "Recommended design:",
                "",
                f"- Primary mode: `{summary['recommended_design']['primary_mode']}`",
                "- Default enabled: `false`",
                "- Runtime active in Step142: `false`",
                "",
            ]
        )
    if summary.get("blocking_reason"):
        lines.extend(["Blocking reason:", "", summary["blocking_reason"], ""])
    if summary.get("missing_input_path"):
        lines.extend(["Missing input:", "", f"- `{summary['missing_input_path']}`", ""])
    return "\n".join(lines)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step141-decision", type=Path, default=DEFAULT_STEP141_DECISION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    run_step142_mass_neutral_design_report(args.step141_decision, args.output_dir, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
