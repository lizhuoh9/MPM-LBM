from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step112_fsi_config_defaults_keep_dynamics_controls_disabled():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    config = FSIDriverConfig()
    assert config.mpm_planar_constraint_mode == "disabled"
    assert config.mpm_planar_constraint_axis == "z"
    assert config.mpm_velocity_damping == 0.0
    assert config.mpm_damping_application == "disabled"


def test_step112_planar_and_damping_controls_reject_invalid_values():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    for kwargs in (
        {"mpm_planar_constraint_mode": "lock_y"},
        {"mpm_planar_constraint_axis": "x"},
        {"mpm_velocity_damping": -1.0},
        {"mpm_damping_application": "always"},
    ):
        try:
            FSIDriverConfig(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid Step112 dynamics control accepted: {kwargs}")


def test_step112_planar_constraint_and_damping_are_mpm_opt_in_source_controls():
    config_source = (ROOT / "src" / "mpm_lbm" / "sim" / "mpm" / "config.py").read_text(encoding="utf-8")
    solid_source = (ROOT / "src" / "mpm_lbm" / "sim" / "mpm" / "solid.py").read_text(encoding="utf-8")
    assert "mpm_planar_constraint_mode" in config_source
    assert "mpm_velocity_damping" in config_source
    assert "apply_step112_dynamics_controls" in solid_source
    assert "self.v[p].z = 0.0" in solid_source
    assert "self.fixed_x[p].z" in solid_source
    assert "mpm_damping_application" in solid_source
