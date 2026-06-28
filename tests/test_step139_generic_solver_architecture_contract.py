import ast
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DOC = ROOT / "docs" / "GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md"
ARCH_DOC = ROOT / "docs" / "01_architecture.md"

CORE_DIRS = [
    ROOT / "src" / "mpm_lbm" / "sim" / "lbm",
    ROOT / "src" / "mpm_lbm" / "sim" / "mpm",
    ROOT / "src" / "mpm_lbm" / "sim" / "coupling",
    ROOT / "src" / "mpm_lbm" / "sim" / "drivers",
    ROOT / "src" / "mpm_lbm" / "sim" / "geometry",
    ROOT / "src" / "mpm_lbm" / "sim" / "monitoring",
]

FORBIDDEN_CORE_IMPORT_PREFIXES = (
    "benchmarks",
    "experiments",
)

FORBIDDEN_RUNTIME_ASSET_TOKENS = (
    "benchmarks/private",
    "benchmarks\\private",
    ".cas.h5",
    ".dat.h5",
    "steady_fluid_flow.jou",
    "fsi_2way.zip",
    "fluent.exe",
    "fluent -g",
)


def test_step139_generic_solver_contract_doc_exists_and_states_boundaries():
    text = _single_spaced(CONTRACT_DOC.read_text(encoding="utf-8"))
    architecture = ARCH_DOC.read_text(encoding="utf-8")

    for phrase in [
        "Solver core remains benchmark-agnostic.",
        "Benchmark adapters may prepare inputs, manifests, and comparisons, but they must not change solver equations.",
        "Official Fluent assets stay outside the repository.",
        "Validation claims require explicit artifacts and gates.",
        "Step139 does not select a 96^3 boundary.",
    ]:
        assert phrase in text
    assert "GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md" in architecture


def test_step139_core_packages_do_not_import_benchmark_surfaces():
    violations = []
    for path in _core_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if _is_forbidden_core_import(module):
                        violations.append((path, module))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if _is_forbidden_core_import(module):
                    violations.append((path, module))

    assert violations == []


def test_step139_core_packages_do_not_depend_on_private_official_assets():
    violations = []
    for path in _core_python_files():
        lower = path.read_text(encoding="utf-8").lower().replace("\\", "/")
        for token in FORBIDDEN_RUNTIME_ASSET_TOKENS:
            normalized = token.lower().replace("\\", "/")
            if normalized in lower:
                violations.append((path, token))

    assert violations == []


def test_step139_no_private_or_proprietary_official_assets_are_tracked():
    tracked = _tracked_files()
    forbidden = [
        path
        for path in tracked
        if path.startswith("benchmarks/private/")
        or path.endswith(".cas.h5")
        or path.endswith(".dat.h5")
        or path.endswith(".cas")
        or path.endswith(".wbpj")
        or path.endswith("flap.msh")
        or path.endswith("steady_fluid_flow.jou")
        or path.endswith("fsi_2way.zip")
    ]

    assert forbidden == []


def _core_python_files():
    files = []
    for directory in CORE_DIRS:
        assert directory.is_dir()
        files.extend(sorted(directory.rglob("*.py")))
    return files


def _single_spaced(text: str) -> str:
    return " ".join(text.split())


def _is_forbidden_core_import(module: str) -> bool:
    return module in FORBIDDEN_CORE_IMPORT_PREFIXES or module.startswith(
        tuple(prefix + "." for prefix in FORBIDDEN_CORE_IMPORT_PREFIXES)
    )


def _tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()
