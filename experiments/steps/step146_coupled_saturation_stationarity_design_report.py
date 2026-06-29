from __future__ import annotations

import argparse
import json
import math
from hashlib import sha256
from pathlib import Path
from typing import Any


STEP = 146
SOURCE_STEP = 145
DEFAULT_OUTPUT_DIR = Path("outputs") / "step146_coupled_saturation_stationarity_design"

SOURCE_INPUT_PATHS = {
    "step145_summary": Path("outputs")
    / "step145_mass_neutral_long_window_forensics"
    / "step145_failure_mechanism_summary.json",
    "step145_saturation": Path("outputs")
    / "step145_mass_neutral_long_window_forensics"
    / "saturation_segment_report.json",
    "step145_stationarity": Path("outputs")
    / "step145_mass_neutral_long_window_forensics"
    / "stationarity_segment_report.json",
    "step145_controller": Path("outputs")
    / "step145_mass_neutral_long_window_forensics"
    / "controller_lag_segment_report.json",
    "step144_decision": Path("outputs")
    / "step144_mass_neutral_final48"
    / "step144_decision_summary.json",
    "step144_comparison": Path("outputs")
    / "step144_mass_neutral_final48"
    / "step144_long_window_comparison.json",
}

RECOMMENDED_DESIGN = "saturation_aware_mass_neutral_relief_with_stationarity_damping"
FALLBACK_DESIGN = "outlet_population_projection_report_only"
RECOMMENDED_PHASE = "planeflux_saturation_stationarity48"
RECOMMENDED_ROW_ROLE = "saturation_stationarity_diagnostic_48"


def run_step146_design_report(
    step145_summary: Path | str = SOURCE_INPUT_PATHS["step145_summary"],
    step145_saturation: Path | str = SOURCE_INPUT_PATHS["step145_saturation"],
    step145_stationarity: Path | str = SOURCE_INPUT_PATHS["step145_stationarity"],
    step145_controller: Path | str = SOURCE_INPUT_PATHS["step145_controller"],
    step144_decision: Path | str = SOURCE_INPUT_PATHS["step144_decision"],
    step144_comparison: Path | str = SOURCE_INPUT_PATHS["step144_comparison"],
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    del force
    paths = {
        "step145_summary": Path(step145_summary),
        "step145_saturation": Path(step145_saturation),
        "step145_stationarity": Path(step145_stationarity),
        "step145_controller": Path(step145_controller),
        "step144_decision": Path(step144_decision),
        "step144_comparison": Path(step144_comparison),
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = [_display_path(path) for path in paths.values() if not path.is_file()]
    if missing:
        summary = _missing_input_summary(paths, missing)
        _write_outputs(output_dir, summary)
        return summary

    context = {key: _read_json(path) for key, path in paths.items()}
    failures = _source_decision_failures(context)
    if failures:
        summary = _blocked_by_source_decision_summary(paths, context, failures)
        _write_outputs(output_dir, summary)
        return summary

    summary = _design_ready_summary(paths, context)
    _write_outputs(output_dir, summary)
    return summary


def _design_ready_summary(paths: dict[str, Path], context: dict[str, dict[str, Any]]) -> dict[str, Any]:
    step145 = context["step145_summary"]
    step144_decision = context["step144_decision"]
    step144_row = _step144_row(context["step144_comparison"])
    saturation = context["step145_saturation"].get("classification") or {}
    stationarity = context["step145_stationarity"].get("classification") or {}
    controller = context["step145_controller"].get("classification") or {}

    summary = _base_payload(paths, status="design_ready")
    summary.update(
        {
            "missing_input": False,
            "design_readiness_present": True,
            "source_step": SOURCE_STEP,
            "source_step145_status": step145.get("status"),
            "source_step145_decision_case": step145.get("decision_case"),
            "source_step145_dominant_failure_mechanism": step145.get("dominant_failure_mechanism"),
            "source_step145_summary_hash": _file_hash(paths["step145_summary"]),
            "source_step144_decision_case": step144_decision.get("decision_case"),
            "source_step144_row_name": step144_row.get("name"),
            "source_step146_500step_probe_allowed": step145.get("step146_500step_probe_allowed"),
            "source_selected_candidate_surface_review_allowed": step145.get(
                "selected_candidate_surface_review_allowed"
            ),
            "source_selected96_execution_allowed": step145.get("selected96_execution_allowed"),
            "source_validation_claim_allowed": step145.get("validation_claim_allowed"),
            "step144_final_mass_abs": _first(
                step145.get("step144_final_mass_abs"),
                step144_row.get("candidate_mass_acceptance_observed_abs"),
            ),
            "step144_flux_imbalance_rel_tail_mean": _first(
                step145.get("step144_flux_imbalance_rel_tail_mean"),
                step144_row.get("flux_imbalance_rel_tail_mean"),
            ),
            "step144_outlet_flux_tail_cv": _first(
                step145.get("step144_outlet_flux_tail_cv"),
                step144_row.get("outlet_flux_tail_cv"),
            ),
            "step144_mass_neutral_feedback_saturation_fraction_tail": _first(
                step145.get("step144_mass_neutral_feedback_saturation_fraction_tail"),
                step144_row.get("mass_neutral_feedback_saturation_fraction_tail"),
            ),
            "tail_controller_authority_ratio_slope": _first(
                step145.get("tail_controller_authority_ratio_slope"),
                controller.get("controller_authority_ratio_tail_slope"),
            ),
            "step145_tail_saturation_mean": saturation.get("tail_saturation_mean"),
            "step145_tail_saturation_final": saturation.get("tail_saturation_final"),
            "step145_stationarity_interpretation": stationarity.get("interpretation"),
            "step145_controller_interpretation": controller.get("interpretation"),
            "recommended_design": RECOMMENDED_DESIGN,
            "fallback_design": FALLBACK_DESIGN,
            "recommended_step147_phase": RECOMMENDED_PHASE,
            "recommended_step147_row_role": RECOMMENDED_ROW_ROLE,
            "max_step147_rows": 4,
            "max_step147_steps": 250,
            "step147_output_interval": 5,
            "step147_candidate_rows": _step147_candidate_rows(),
            "design_options": _design_options(),
            "design_decision": (
                "Recommend Design A for a later bounded Step147 48^3 / 250-step "
                "diagnostic. Keep Design B as fallback telemetry. Step146 does not "
                "execute either design."
            ),
            "next_step_recommendation": (
                "Step147 may propose at most four bounded 48^3 / 250-step rows for "
                "mass-neutral relief with stationarity damping; selected96 and a "
                "Step146 500-step probe remain blocked."
            ),
        }
    )
    return summary


def _missing_input_summary(paths: dict[str, Path], missing: list[str]) -> dict[str, Any]:
    summary = _base_payload(paths, status="missing_input")
    summary.update(
        {
            "missing_input": True,
            "missing_inputs": missing,
            "design_readiness_present": False,
            "source_step145_decision_case": None,
            "source_step145_dominant_failure_mechanism": None,
            "source_step144_decision_case": None,
            "recommended_design": None,
            "fallback_design": None,
            "recommended_step147_phase": None,
            "recommended_step147_row_role": None,
            "step147_250step_diagnostic_proposal_allowed": False,
            "next_step_recommendation": "Provide all Step145 and Step144 source artifacts before design readiness.",
        }
    )
    return summary


def _blocked_by_source_decision_summary(
    paths: dict[str, Path],
    context: dict[str, dict[str, Any]],
    failures: list[str],
) -> dict[str, Any]:
    step145 = context["step145_summary"]
    step144_decision = context["step144_decision"]
    summary = _base_payload(paths, status="blocked_by_source_decision")
    summary.update(
        {
            "missing_input": False,
            "source_decision_failures": failures,
            "design_readiness_present": False,
            "source_step145_decision_case": step145.get("decision_case"),
            "source_step145_dominant_failure_mechanism": step145.get("dominant_failure_mechanism"),
            "source_step144_decision_case": step144_decision.get("decision_case"),
            "recommended_design": None,
            "fallback_design": None,
            "recommended_step147_phase": None,
            "recommended_step147_row_role": None,
            "step147_250step_diagnostic_proposal_allowed": False,
            "next_step_recommendation": (
                "Keep Step146 blocked until Step145/Step144 source decisions match the "
                "coupled saturation-stationarity design contract."
            ),
        }
    )
    return summary


def _base_payload(paths: dict[str, Path], status: str) -> dict[str, Any]:
    return {
        "artifact": "step146_coupled_saturation_stationarity_design_readiness",
        "step": STEP,
        "status": status,
        "source_input_paths": {key: _display_path(path) for key, path in paths.items()},
        "input_hashes": {
            key: _file_hash(path) for key, path in paths.items() if path.is_file()
        },
        "design_only": True,
        "artifact_only": True,
        "new_lbm_run_executed": False,
        "new_parameter_tuning_executed": False,
        "step121_phase_added": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "selected_candidate_surface_review_allowed": False,
        "validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "figure29_3_parity_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "step146_500step_probe_allowed": False,
        "step147_250step_diagnostic_proposal_allowed": True,
    }


def _source_decision_failures(context: dict[str, dict[str, Any]]) -> list[str]:
    step145 = context["step145_summary"]
    step144_decision = context["step144_decision"]
    checks = {
        "source_step145_decision_case": (
            step145.get("decision_case") == "mixed_saturation_stationarity_failure"
        ),
        "source_step145_dominant_failure_mechanism": (
            step145.get("dominant_failure_mechanism") == "mixed_saturation_stationarity_failure"
        ),
        "source_step146_500step_probe_allowed": (
            step145.get("step146_500step_probe_allowed") is False
        ),
        "source_selected_candidate_surface_review_allowed": (
            step145.get("selected_candidate_surface_review_allowed") is False
        ),
        "source_selected96_execution_allowed": step145.get("selected96_execution_allowed") is False,
        "source_validation_claim_allowed": step145.get("validation_claim_allowed") is False,
        "source_step144_decision_case": (
            step144_decision.get("decision_case")
            == "mass_neutral_flow_stationarity_long_window_failure"
        ),
    }
    return [key for key, passed in checks.items() if not passed]


def _step147_candidate_rows() -> list[dict[str, Any]]:
    return [
        {
            "name": "mass_neutral_high_baseline",
            "gain_mass": 0.50,
            "cap_mass": 0.00100,
            "blend": 1.0,
            "stationarity_damping": "current Step144/Step143 high setting baseline",
            "role": "baseline repeat only",
        },
        {
            "name": "relief_low",
            "gain_mass": 0.35,
            "cap_mass": 0.00100,
            "blend": 0.50,
            "stationarity_damping": "stronger damping; prefer slew_alpha = 0.25 or delta_cap_u = 0.00025",
            "role": "mass-neutral relief plus stationarity damping",
        },
        {
            "name": "relief_mid",
            "gain_mass": 0.50,
            "cap_mass": 0.00100,
            "blend": 0.50,
            "stationarity_damping": "stronger damping",
            "role": "same gain/cap with lower blend",
        },
        {
            "name": "relief_cap_test",
            "gain_mass": 0.50,
            "cap_mass": 0.00150,
            "blend": 0.50,
            "stationarity_damping": "stronger damping",
            "role": "diagnostic cap test only; not promotion",
        },
    ]


def _design_options() -> list[dict[str, Any]]:
    return [
        {
            "name": RECOMMENDED_DESIGN,
            "label": "Design A",
            "recommended_for_step147": True,
            "runtime_activation_in_step146": False,
            "description": (
                "Couple mass-neutral relief to stationarity damping instead of "
                "raising the mass cap alone."
            ),
        },
        {
            "name": FALLBACK_DESIGN,
            "label": "Design B",
            "recommended_for_step147": False,
            "runtime_activation_in_step146": False,
            "description": (
                "Keep outlet population projection as report-only feasibility "
                "telemetry before any runtime activation."
            ),
        },
    ]


def _step144_row(comparison: dict[str, Any]) -> dict[str, Any]:
    rows = comparison.get("rows") or []
    return dict(rows[0]) if rows else {}


def _write_outputs(output_dir: Path, summary: dict[str, Any]) -> None:
    _write_json(output_dir / "step146_design_readiness_report.json", summary)
    _write_markdown_summary(output_dir / "step146_design_readiness_report.md", summary)


def _write_markdown_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Step146 Design Readiness Report",
        "",
        f"Status: `{summary['status']}`.",
        "",
        f"Design-only: `{str(summary['design_only']).lower()}`.",
        f"Artifact-only: `{str(summary['artifact_only']).lower()}`.",
        f"New LBM run executed: `{str(summary['new_lbm_run_executed']).lower()}`.",
        f"Step121 phase added: `{str(summary['step121_phase_added']).lower()}`.",
        f"selected96 execution allowed: `{str(summary['selected96_execution_allowed']).lower()}`.",
        (
            "Selected-candidate-surface review allowed: "
            f"`{str(summary['selected_candidate_surface_review_allowed']).lower()}`."
        ),
        f"Validation claim allowed: `{str(summary['validation_claim_allowed']).lower()}`.",
        f"Step146 500-step probe allowed: `{str(summary['step146_500step_probe_allowed']).lower()}`.",
        "",
    ]
    if summary["status"] == "missing_input":
        lines.extend(["Missing inputs:", ""])
        lines.extend(f"- `{item}`" for item in summary.get("missing_inputs", []))
    elif summary["status"] == "blocked_by_source_decision":
        lines.extend(["Blocked by source decision:", ""])
        lines.extend(f"- `{item}`" for item in summary.get("source_decision_failures", []))
    else:
        lines.extend(
            [
                f"Source Step145 decision: `{summary['source_step145_decision_case']}`.",
                f"Source Step144 decision: `{summary['source_step144_decision_case']}`.",
                "",
                "Design A is recommended for a later Step147 bounded diagnostic:",
                "",
                f"- `{summary['recommended_design']}`",
                f"- Step147 phase proposal: `{summary['recommended_step147_phase']}`",
                f"- Step147 row role proposal: `{summary['recommended_step147_row_role']}`",
                f"- Max rows: `{summary['max_step147_rows']}`",
                f"- Max steps: `{summary['max_step147_steps']}`",
                "",
                "Design B remains fallback telemetry only:",
                "",
                f"- `{summary['fallback_design']}`",
                "",
                "Current blocked state:",
                "",
                "- selected96 remains blocked.",
                "- selected-candidate-surface review remains blocked.",
                "- validation claim remains blocked.",
                "- 500-step probe remains blocked.",
                "",
                "Artifact facts:",
                "",
                f"- Step144 final mass abs: `{summary['step144_final_mass_abs']}`",
                (
                    "- Step144 mean flux imbalance tail: "
                    f"`{summary['step144_flux_imbalance_rel_tail_mean']}`"
                ),
                f"- Step144 outlet flux tail CV: `{summary['step144_outlet_flux_tail_cv']}`",
                (
                    "- Step144 mass-neutral saturation tail: "
                    f"`{summary['step144_mass_neutral_feedback_saturation_fraction_tail']}`"
                ),
                (
                    "- Tail controller authority ratio slope: "
                    f"`{summary['tail_controller_authority_ratio_slope']}`"
                ),
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(_jsonable(payload), f, indent=2, sort_keys=True)
        f.write("\n")


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path | str) -> str:
    path = Path(path)
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _first(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return _display_path(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Step146 artifact-only coupled design readiness")
    parser.add_argument("--step145-summary", type=Path, default=SOURCE_INPUT_PATHS["step145_summary"])
    parser.add_argument("--step145-saturation", type=Path, default=SOURCE_INPUT_PATHS["step145_saturation"])
    parser.add_argument(
        "--step145-stationarity",
        type=Path,
        default=SOURCE_INPUT_PATHS["step145_stationarity"],
    )
    parser.add_argument("--step145-controller", type=Path, default=SOURCE_INPUT_PATHS["step145_controller"])
    parser.add_argument("--step144-decision", type=Path, default=SOURCE_INPUT_PATHS["step144_decision"])
    parser.add_argument("--step144-comparison", type=Path, default=SOURCE_INPUT_PATHS["step144_comparison"])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    summary = run_step146_design_report(
        step145_summary=args.step145_summary,
        step145_saturation=args.step145_saturation,
        step145_stationarity=args.step145_stationarity,
        step145_controller=args.step145_controller,
        step144_decision=args.step144_decision,
        step144_comparison=args.step144_comparison,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if summary.get("status") == "design_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
