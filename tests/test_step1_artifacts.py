from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_log(path):
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="ignore")


def test_step1_required_artifacts_exist():
    required_paths = [
        "STEP1_ENVIRONMENT_AND_BASELINE_GOAL.md",
        "STEP1_BASELINE_REPORT.md",
        "requirements.txt",
        "environment.yml",
        "baseline_tests/check_taichi_backend.py",
        "baseline_tests/run_lbm_cavity_baseline.py",
        "baseline_tests/run_mpm3d_baseline.py",
        "logs/check_taichi_backend.log",
        "logs/lbm_cavity_baseline.log",
        "logs/mpm3d_baseline.log",
        "outputs/lbm_cavity/LB_SingelPhase_500.vtr",
        "outputs/mpm3d/mpm3d_positions.npy",
        "external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step1_logs_record_successful_gpu_baselines():
    backend_log = read_log(ROOT / "logs/check_taichi_backend.log")
    lbm_log = read_log(ROOT / "logs/lbm_cavity_baseline.log")
    mpm_log = read_log(ROOT / "logs/mpm3d_baseline.log")

    assert "CPU: OK" in backend_log
    assert "GPU: OK" in backend_log
    assert "Starting on arch=cuda" in lbm_log
    assert "[OK] LBM cavity baseline finished" in lbm_log
    assert "rho_min=1.000000e+00" in lbm_log
    assert "Starting on arch=cuda" in mpm_log
    assert "[OK] MPM 3D baseline finished" in mpm_log


def test_step1_report_marks_acceptance_complete():
    report = (ROOT / "STEP1_BASELINE_REPORT.md").read_text(encoding="utf-8")

    assert "- [x] Taichi GPU backend runs successfully" in report
    assert "- [x] LBM writes VTK output" in report
    assert "- [x] MPM `J` remains positive" in report
    assert "- [x] Yes" in report
