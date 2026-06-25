import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.duct_flap_proxy import (
    duct_flap_proxy_component_masks,
    duct_flap_proxy_static_geometry,
)
from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D


def mirrored_geometry_config(n_particles=128):
    return GeometryConfig(
        geometry_type="duct_flap_proxy",
        n_particles=n_particles,
        particles_per_axis_hint=64,
        duct={"x": [0.0, 1.0], "y": [0.3, 0.7], "z": [0.45, 0.55]},
        flap={
            "anchor_x": 0.505,
            "anchor_y": 0.3,
            "height_over_duct_height": 0.25,
            "thickness_over_duct_height": 0.075,
            "normalized_height": 0.10,
            "normalized_thickness": 0.03,
            "z": [0.45, 0.55],
            "fixed_base": True,
            "mirrored_pair": True,
        },
        material_reference={
            "density": 1600.0,
            "youngs_modulus": 1.0e6,
            "poisson_ratio": 0.47,
            "used_for_exact_structural_model": False,
            "used_for_mpm_config": True,
        },
    )


def test_step113_default_duct_flap_proxy_stays_single_flap():
    cloud = GeometrySampler3D(GeometryConfig(geometry_type="duct_flap_proxy", n_particles=64)).sample_particles()

    assert cloud["sampling_stats"]["flap_count"] == 1


def test_step113_mirrored_pair_exposes_two_flaps_to_sampler():
    cloud = GeometrySampler3D(mirrored_geometry_config()).sample_particles()

    assert cloud["sampling_stats"]["flap_count"] == 2
    assert int(np.count_nonzero(cloud["fixed_base_mask"])) > 0
    assert int(np.count_nonzero(cloud["free_tip_proxy_mask"])) > 0


def test_step113_mirrored_component_masks_include_upper_and_lower_flaps():
    config = mirrored_geometry_config(n_particles=16)
    points = np.array(
        [
            [0.505, 0.315, 0.500],
            [0.505, 0.385, 0.500],
            [0.505, 0.685, 0.500],
            [0.505, 0.615, 0.500],
            [0.200, 0.500, 0.500],
        ],
        dtype=np.float64,
    )

    masks = duct_flap_proxy_component_masks(points, config)

    assert masks["flap"].tolist() == [True, True, True, True, False]
    assert masks["fixed_base"].tolist() == [True, False, True, False, False]
    assert masks["free_tip_proxy"].tolist() == [False, True, False, True, False]


def test_step113_static_geometry_can_voxelize_mirrored_pair_when_requested():
    solid, report = duct_flap_proxy_static_geometry(64, mirrored_geometry_config(n_particles=16), include_flap=True)

    assert solid.shape == (64, 64, 64)
    assert report["flap_count"] == 2
    assert report["flap_static_cell_count"] > 0
    assert report["all_fluid_geometry_used"] is False
