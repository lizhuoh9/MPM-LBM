from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_step11_required_documentation_paths_exist():
    required_paths = [
        "README.md",
        "docs/00_project_status.md",
        "docs/01_architecture.md",
        "docs/02_numerical_methods.md",
        "docs/03_units_grid_timestep.md",
        "docs/04_fsi_modes.md",
        "docs/05_running_baselines.md",
        "docs/06_results_summary.md",
        "docs/07_limitations.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "configs/README.md",
        "paper/technical_report_draft.md",
        "paper/figures/README.md",
        "STEP11_WRITING_MODULE_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step11_readme_contract():
    readme = read_text("README.md")

    required_keywords = [
        "MPM-LBM",
        "Taichi",
        "engineering prototype",
        "FSIDriver3D",
        "none",
        "penalty",
        "moving_boundary",
        "not production",
        "two-phase flow",
        "contact angle",
        "squid geometry",
        "strict momentum-conserving",
        "taichi_LBM3D",
        "external/taichi_LBM3D",
    ]

    missing = [keyword for keyword in required_keywords if keyword not in readme]
    assert missing == []


def test_step11_limitations_contract():
    limitations = read_text("docs/07_limitations.md")

    required_keywords = [
        "single-phase",
        "engineering scale",
        "not strict",
        "no real squid geometry",
        "dense grid",
        "small-scale",
        "n_grid = 32",
        "n_particles = 4096",
    ]

    missing = [keyword for keyword in required_keywords if keyword not in limitations]
    assert missing == []


def test_step11_api_reference_contract():
    api_reference = read_text("docs/09_api_reference.md")

    required_keywords = [
        "LBMFluid3D",
        "MPMSolid3D",
        "GridUnitMapper",
        "UnifiedSimConfig",
        "MPMToLBMProjector3D",
        "PenaltyFSICoupler3D",
        "MovingBoundaryFSICoupler3D",
        "FSIDriverConfig",
        "FSIDriver3D",
        "FSIDiagnostics3D",
        "purpose",
        "main fields",
        "main methods",
        "mode",
    ]

    missing = [keyword for keyword in required_keywords if keyword not in api_reference]
    assert missing == []


def test_step11_results_summary_contract():
    results = read_text("docs/06_results_summary.md")

    required_keywords = [
        "projection_zone_ux_final",
        "moving_boundary",
        "penalty",
        "none",
        "1.293938956e-03",
        "3.118396126e-05",
        "performance",
        "4.373437290e+01",
        "1.652768771e+02",
        "7.204992740e+01",
        "small-scale engineering baselines",
        "not final accuracy validation",
    ]

    missing = [keyword for keyword in required_keywords if keyword not in results]
    assert missing == []


def test_step11_technical_report_contract():
    report = read_text("paper/technical_report_draft.md")

    required_headings = [
        "# A Taichi-based Prototype for 3D MPM-LBM Fluid-Solid Coupling",
        "## Abstract",
        "## 1. Introduction",
        "## 2. System Architecture",
        "## 3. Numerical Methods",
        "## 4. Coupling Modes",
        "## 5. Validation Baselines",
        "## 6. Results",
        "## 7. Limitations",
        "## 8. Future Work",
        "## Appendix A: Reproducibility Commands",
        "## Appendix B: Configuration Examples",
    ]
    missing_headings = [heading for heading in required_headings if heading not in report]
    assert missing_headings == []

    required_abstract_terms = [
        "Taichi-based prototype",
        "3D MPM solid solver",
        "single-phase D3Q19 MRT LBM fluid solver",
        "penalty-force mode",
        "moving-boundary bounce-back mode",
        "unified driver",
        "32^3",
        "4096",
        "not final strict momentum-conserving",
        "no two-phase flow",
        "contact-angle physics",
        "real squid geometry",
    ]
    missing_terms = [term for term in required_abstract_terms if term not in report]
    assert missing_terms == []


def test_step11_documentation_avoids_overclaims():
    doc_paths = [
        "README.md",
        "docs/00_project_status.md",
        "docs/01_architecture.md",
        "docs/02_numerical_methods.md",
        "docs/03_units_grid_timestep.md",
        "docs/04_fsi_modes.md",
        "docs/05_running_baselines.md",
        "docs/06_results_summary.md",
        "docs/07_limitations.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "configs/README.md",
        "paper/technical_report_draft.md",
        "paper/figures/README.md",
    ]
    forbidden_claims = [
        "is a production-grade solver",
        "fully validated sharp-interface FSI",
        "real squid simulation is validated",
        "strict momentum-conserving FSI is complete",
    ]

    offenders = []
    for path in doc_paths:
        text = read_text(path)
        offenders.extend(f"{path}: {claim}" for claim in forbidden_claims if claim in text)

    assert offenders == []


def test_step11_report_acceptance_complete():
    report = read_text("STEP11_WRITING_MODULE_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 11 final commit",
        "- [x] README.md exists",
        "- [x] README.md states current status is engineering prototype",
        "- [x] README.md lists none / penalty / moving_boundary",
        "- [x] README.md lists not-implemented items",
        "- [x] README.md includes upstream taichi_LBM3D note",
        "- [x] docs/00_project_status.md exists",
        "- [x] docs/01_architecture.md exists",
        "- [x] docs/02_numerical_methods.md exists",
        "- [x] docs/03_units_grid_timestep.md exists",
        "- [x] docs/04_fsi_modes.md exists",
        "- [x] docs/05_running_baselines.md exists",
        "- [x] docs/06_results_summary.md exists",
        "- [x] docs/07_limitations.md exists",
        "- [x] docs/08_roadmap.md exists",
        "- [x] docs/09_api_reference.md exists",
        "- [x] configs/README.md exists",
        "- [x] paper/technical_report_draft.md exists",
        "- [x] paper/figures/README.md exists",
        "- [x] docs explain moving-boundary reaction uses engineering scale",
        "- [x] docs state the project is not strict final momentum-conserving sharp-interface FSI",
        "- [x] docs state there is no real squid geometry",
        "- [x] docs state single-phase only",
        "- [x] Step 10 mode matrix results are included in results summary",
        "- [x] Step 10 performance profile is included in results summary",
        "- [x] API reference includes all main classes",
        "- [x] tests/test_step11_documentation_contract.py exists",
        "- [x] documentation contract test passes",
        "- [x] pytest -q passes",
        "- [x] logs/step11_pytest.log exists",
        "- [x] no new solver code",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no overclaims about production-grade or fully validated sharp-interface FSI",
        "- [x] STEP11_WRITING_MODULE_REPORT.md is complete",
        "- [x] Step 11 artifacts are committed",
        "- [x] Step 11 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
