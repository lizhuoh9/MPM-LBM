from __future__ import annotations

import re
from pathlib import Path


AUDITED_PATTERNS = ("tests/test_step*.py", "baseline_tests/run_step*.py")
ALLOWED_TEST_STRENGTH_LEVELS = {
    "artifact_contract",
    "artifact_plus_source_contract",
    "runner_reexecution_contract",
    "proxy_diagnostic_contract",
    "solver_smoke_contract",
    "formula_unit_contract",
    "numerical_benchmark_contract",
}
PYTEST_RESULT_INTERPRETATION = (
    "A passing full pytest run means contract/artifact/proxy/solver-smoke tests passed "
    "according to the test strength audit classification."
)


def build_repository_test_strength_audit(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = [test_strength_row(root, path) for path in audited_paths(root)]
    rows.sort(key=lambda row: (int(row["step"]), row["test_file"]))
    summary = {
        "audited_file_count": len(rows),
        "classified_file_count": sum(1 for row in rows if row["test_strength_level"]),
        "artifact_or_proxy_contract_count": sum(
            1
            for row in rows
            if row["test_strength_level"]
            in {
                "artifact_contract",
                "artifact_plus_source_contract",
                "proxy_diagnostic_contract",
            }
        ),
        "runner_reexecution_contract_count": sum(1 for row in rows if row["reruns_runner"]),
        "solver_runtime_contract_count": sum(1 for row in rows if row["reruns_solver"]),
        "formula_unit_contract_count": sum(1 for row in rows if row["validates_formula"]),
        "numerical_benchmark_contract_count": sum(1 for row in rows if row["validates_numerical_benchmark"]),
        "test_suite_result_interpretation": PYTEST_RESULT_INTERPRETATION,
        "allowed_test_strength_level_count": len(ALLOWED_TEST_STRENGTH_LEVELS),
        "out_of_policy_strength_level_count": sum(
            1 for row in rows if row["test_strength_level"] not in ALLOWED_TEST_STRENGTH_LEVELS
        ),
        "test_strength_audit_pass": False,
    }
    summary["test_strength_audit_pass"] = bool(
        summary["audited_file_count"] > 0
        and summary["audited_file_count"] == summary["classified_file_count"]
        and summary["artifact_or_proxy_contract_count"] > 0
        and summary["runner_reexecution_contract_count"] > 0
        and summary["out_of_policy_strength_level_count"] == 0
    )
    return rows, summary


def audited_paths(root: Path) -> list[Path]:
    paths = []
    for pattern in AUDITED_PATTERNS:
        paths.extend(path for path in root.glob(pattern) if path.is_file())
    return paths


def test_strength_row(root: Path, path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    rel = path.relative_to(root).as_posix()
    is_runner = rel.startswith("baseline_tests/run_step")
    step = step_from_name(path.name)
    checks_file_existence = any(token in lower for token in [".is_file(", ".exists(", "required_files", "output_files"])
    checks_log_marker = "log_markers" in lower or "marker" in lower or "logs/" in lower
    checks_report_text = "read_text" in lower and (".md" in lower or "report" in lower or "docs/" in lower)
    checks_committed_artifact_json = ".json" in lower and ("read_json" in lower or "json.load" in lower)
    checks_source_string = "read_text" in lower and ("src/" in lower or "\\src\\" in lower or "source" in lower)
    reruns_runner = is_runner or "subprocess" in lower or "run_step" in lower
    reruns_solver = any(token in lower for token in ["fsidriver", "driver.run", "run_simulation", "run_baseline"])
    validates_formula = any(token in lower for token in ["formula", "tau_from_", "relaxation", "viscosity", "area_scale", "bounceback"])
    validates_numerical_benchmark = any(token in lower for token in ["numerical_benchmark", "analytic", "couette", "benchmark"])
    return {
        "test_file": rel,
        "step": step,
        "checks_file_existence": checks_file_existence,
        "checks_log_marker": checks_log_marker,
        "checks_report_text": checks_report_text,
        "checks_committed_artifact_json": checks_committed_artifact_json,
        "checks_source_string": checks_source_string,
        "reruns_runner": reruns_runner,
        "reruns_solver": reruns_solver,
        "validates_formula": validates_formula,
        "validates_numerical_benchmark": validates_numerical_benchmark,
        "test_strength_level": classify_strength(
            step=step,
            is_runner=is_runner,
            checks_committed_artifact_json=checks_committed_artifact_json,
            checks_source_string=checks_source_string,
            checks_report_text=checks_report_text,
            checks_log_marker=checks_log_marker,
            checks_file_existence=checks_file_existence,
            reruns_solver=reruns_solver,
            validates_formula=validates_formula,
            validates_numerical_benchmark=validates_numerical_benchmark,
        ),
    }


def classify_strength(
    *,
    step: int,
    is_runner: bool,
    checks_committed_artifact_json: bool,
    checks_source_string: bool,
    checks_report_text: bool,
    checks_log_marker: bool,
    checks_file_existence: bool,
    reruns_solver: bool,
    validates_formula: bool,
    validates_numerical_benchmark: bool,
) -> str:
    if validates_numerical_benchmark:
        return "numerical_benchmark_contract"
    if reruns_solver:
        return "solver_smoke_contract"
    if step in {50, 51, 52}:
        return "proxy_diagnostic_contract"
    if validates_formula:
        return "formula_unit_contract"
    if is_runner:
        return "runner_reexecution_contract"
    if checks_committed_artifact_json and checks_source_string:
        return "artifact_plus_source_contract"
    if checks_committed_artifact_json:
        return "artifact_contract"
    if checks_report_text or checks_log_marker:
        return "artifact_contract"
    if checks_file_existence:
        return "artifact_contract"
    return "artifact_contract"


def step_from_name(name: str) -> int:
    match = re.search(r"[Ss][Tt][Ee][Pp](\d+)", name)
    return int(match.group(1)) if match else -1
