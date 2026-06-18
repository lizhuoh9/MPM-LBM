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


def test_step3_required_artifacts_exist():
    required_paths = [
        "src/mpm_config.py",
        "src/mpm_solid.py",
        "baseline_tests/run_mpm_rest_block.py",
        "baseline_tests/run_mpm_falling_block.py",
        "baseline_tests/run_mpm_elastic_block.py",
        "logs/step3_mpm_rest_block.log",
        "logs/step3_mpm_falling_block.log",
        "logs/step3_mpm_elastic_block.log",
        "outputs/mpm_rest_block/particles_x.npy",
        "outputs/mpm_rest_block/particles_v.npy",
        "outputs/mpm_rest_block/particles_F.npy",
        "outputs/mpm_rest_block/particles_J.npy",
        "outputs/mpm_falling_block/particles_x.npy",
        "outputs/mpm_falling_block/particles_v.npy",
        "outputs/mpm_falling_block/particles_F.npy",
        "outputs/mpm_falling_block/particles_J.npy",
        "outputs/mpm_elastic_block/particles_x.npy",
        "outputs/mpm_elastic_block/particles_v.npy",
        "outputs/mpm_elastic_block/particles_F.npy",
        "outputs/mpm_elastic_block/particles_J.npy",
        "STEP3_MPM_SOLID_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step3_source_contains_required_interfaces():
    init_source = (ROOT / "src/__init__.py").read_text(encoding="utf-8")
    config_source = (ROOT / "src/mpm_config.py").read_text(encoding="utf-8")
    solid_source = (ROOT / "src/mpm_solid.py").read_text(encoding="utf-8")
    lbm_source = (ROOT / "src/lbm_fluid.py").read_text(encoding="utf-8")

    assert "class MPMConfig" in config_source
    assert "class MPMSolid3D" in solid_source
    assert "def init_box" in solid_source
    assert "def clear_grid" in solid_source
    assert "def p2g" in solid_source
    assert "def grid_update" in solid_source
    assert "def g2p" in solid_source
    assert "def substep" in solid_source
    assert "def get_stats" in solid_source
    assert "def export_particles" in solid_source
    assert "ti.svd" in solid_source
    assert "self.F" in solid_source
    assert "self.Jp" in solid_source
    assert "MPMConfig" in init_source
    assert "MPMSolid3D" in init_source
    assert "Diagnostic-only" in lbm_source
    assert "ti.cast(new_solid, ti.i8)" in lbm_source
    assert "ti.cast(0, ti.i8)" in lbm_source
    assert "ti.cast(1, ti.i8)" in lbm_source


def test_step3_logs_record_successful_baselines():
    rest_log = read_log(ROOT / "logs/step3_mpm_rest_block.log")
    falling_log = read_log(ROOT / "logs/step3_mpm_falling_block.log")
    elastic_log = read_log(ROOT / "logs/step3_mpm_elastic_block.log")
    dynamic_log = read_log(ROOT / "logs/step2_lbm_refactor_dynamic_solid.log")

    assert "Starting on arch=cuda" in rest_log
    assert "step=0100" in rest_log
    assert "[OK] Step 3 MPM rest block baseline finished" in rest_log

    assert "Starting on arch=cuda" in falling_log
    assert "step=0100" in falling_log
    assert "[OK] Step 3 MPM falling block baseline finished" in falling_log

    assert "Starting on arch=cuda" in elastic_log
    assert "step=0300" in elastic_log
    assert "[OK] Step 3 MPM elastic block baseline finished" in elastic_log

    assert "Assign may lose precision: i8 <- i32" not in dynamic_log


def test_step3_report_marks_acceptance_complete():
    report = (ROOT / "STEP3_MPM_SOLID_REPORT.md").read_text(encoding="utf-8")

    assert "- [x] Step 2 i8 warning cleanup implemented" in report
    assert "- [x] `src/mpm_config.py` exists" in report
    assert "- [x] `src/mpm_solid.py` exists" in report
    assert "- [x] `MPMSolid3D` can initialize" in report
    assert "- [x] Rest block baseline completes" in report
    assert "- [x] Falling block baseline completes" in report
    assert "- [x] Elastic block baseline completes" in report
    assert "- [x] Particle x/v/F/J `.npy` outputs exist for each baseline" in report
    assert "- [x] `pytest` passes" in report
    assert "- [x] Yes" in report
