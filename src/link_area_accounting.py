"""Diagnostic-only link-area proxy accounting for moving-boundary bounce-back."""

import os
import numpy as np


VALID_AREA_POLICIES = ("uniform", "inverse_length", "length")


class LinkAreaMomentumAccounting3D:
    """
    Diagnostic-only link-area proxy accounting for moving-boundary bounce-back.
    Does not modify solver state.
    """

    @staticmethod
    def direction_metadata(lbm):
        e = lbm.e.to_numpy().astype(np.float64)
        lengths = np.linalg.norm(e, axis=1)
        manhattan = np.sum(np.abs(e), axis=1)
        direction_class = np.empty(e.shape[0], dtype=object)
        for i, norm1 in enumerate(manhattan):
            if norm1 == 0:
                direction_class[i] = "rest"
            elif norm1 == 1:
                direction_class[i] = "axis"
            elif norm1 == 2:
                direction_class[i] = "face_diagonal"
            else:
                raise RuntimeError(f"unexpected D3Q19 direction at index {i}: {e[i]}")

        return {
            "e": e,
            "length": lengths,
            "direction_class": direction_class,
            "is_rest": direction_class == "rest",
            "is_axis": direction_class == "axis",
            "is_face_diagonal": direction_class == "face_diagonal",
        }

    @staticmethod
    def area_weights(lbm, policy="inverse_length"):
        if policy not in VALID_AREA_POLICIES:
            raise ValueError(f"policy must be one of {VALID_AREA_POLICIES}")

        metadata = LinkAreaMomentumAccounting3D.direction_metadata(lbm)
        lengths = metadata["length"]
        weights = np.zeros_like(lengths, dtype=np.float64)
        active = ~metadata["is_rest"]

        if policy == "uniform":
            weights[active] = 1.0
        elif policy == "inverse_length":
            weights[active] = 1.0 / lengths[active]
        elif policy == "length":
            weights[active] = lengths[active]

        return weights

    @staticmethod
    def read_directional_stats(lbm):
        stats = lbm.get_moving_boundary_directional_stats()
        return {
            "link_count_by_dir": np.asarray(stats["link_count_by_dir"], dtype=np.int64),
            "fluid_impulse_by_dir": np.asarray(stats["fluid_impulse_by_dir"], dtype=np.float64),
            "solid_force_by_dir": np.asarray(stats["solid_force_by_dir"], dtype=np.float64),
            "correction_abs_sum_by_dir": np.asarray(stats["correction_abs_sum_by_dir"], dtype=np.float64),
            "correction_abs_max_by_dir": np.asarray(stats["correction_abs_max_by_dir"], dtype=np.float64),
        }

    @staticmethod
    def area_weighted_impulse(lbm, policy="inverse_length"):
        directional = LinkAreaMomentumAccounting3D.read_directional_stats(lbm)
        weights = LinkAreaMomentumAccounting3D.area_weights(lbm, policy=policy)
        weighted_fluid = np.sum(directional["fluid_impulse_by_dir"] * weights[:, None], axis=0, dtype=np.float64)
        weighted_solid = np.sum(directional["solid_force_by_dir"] * weights[:, None], axis=0, dtype=np.float64)
        return {
            "policy": policy,
            "area_weighted_fluid_impulse": weighted_fluid,
            "area_weighted_solid_force": weighted_solid,
            "area_weighted_balance": weighted_fluid + weighted_solid,
            "area_weights": weights,
        }

    @staticmethod
    def summarize_link_accounting(lbm, policy="inverse_length"):
        metadata = LinkAreaMomentumAccounting3D.direction_metadata(lbm)
        directional = LinkAreaMomentumAccounting3D.read_directional_stats(lbm)
        weighted = LinkAreaMomentumAccounting3D.area_weighted_impulse(lbm, policy=policy)
        scalar = lbm.get_moving_boundary_stats()

        link_count = directional["link_count_by_dir"]
        fluid_by_dir = directional["fluid_impulse_by_dir"]
        solid_by_dir = directional["solid_force_by_dir"]
        weights = weighted["area_weights"]
        directional_fluid = np.sum(fluid_by_dir, axis=0, dtype=np.float64)
        directional_solid = np.sum(solid_by_dir, axis=0, dtype=np.float64)
        scalar_fluid = np.asarray(scalar["bb_net_fluid_impulse"], dtype=np.float64)
        scalar_solid = np.asarray(scalar["bb_net_solid_force"], dtype=np.float64)
        hydro_sum = np.sum(lbm.hydro_force.to_numpy().reshape(-1, 3), axis=0, dtype=np.float64)

        axis_link_count = int(np.sum(link_count[metadata["is_axis"]]))
        face_diagonal_link_count = int(np.sum(link_count[metadata["is_face_diagonal"]]))
        area_proxy_total = float(np.sum(link_count * weights))
        scalar_vs_directional_impulse_error = scalar_fluid - directional_fluid
        scalar_vs_directional_solid_error = scalar_solid - directional_solid
        hydro_vs_directional_solid_error = hydro_sum - directional_solid

        return {
            "policy": policy,
            "total_link_count": int(np.sum(link_count)),
            "axis_link_count": axis_link_count,
            "face_diagonal_link_count": face_diagonal_link_count,
            "area_proxy_total": area_proxy_total,
            "bb_net_fluid_impulse_x": float(scalar_fluid[0]),
            "bb_net_fluid_impulse_y": float(scalar_fluid[1]),
            "bb_net_fluid_impulse_z": float(scalar_fluid[2]),
            "bb_net_solid_force_x": float(scalar_solid[0]),
            "bb_net_solid_force_y": float(scalar_solid[1]),
            "bb_net_solid_force_z": float(scalar_solid[2]),
            "directional_fluid_impulse_x": float(directional_fluid[0]),
            "directional_fluid_impulse_y": float(directional_fluid[1]),
            "directional_fluid_impulse_z": float(directional_fluid[2]),
            "directional_solid_force_x": float(directional_solid[0]),
            "directional_solid_force_y": float(directional_solid[1]),
            "directional_solid_force_z": float(directional_solid[2]),
            "area_weighted_fluid_impulse_x": float(weighted["area_weighted_fluid_impulse"][0]),
            "area_weighted_fluid_impulse_y": float(weighted["area_weighted_fluid_impulse"][1]),
            "area_weighted_fluid_impulse_z": float(weighted["area_weighted_fluid_impulse"][2]),
            "area_weighted_solid_force_x": float(weighted["area_weighted_solid_force"][0]),
            "area_weighted_solid_force_y": float(weighted["area_weighted_solid_force"][1]),
            "area_weighted_solid_force_z": float(weighted["area_weighted_solid_force"][2]),
            "area_weighted_balance_error_x": float(weighted["area_weighted_balance"][0]),
            "area_weighted_balance_error_y": float(weighted["area_weighted_balance"][1]),
            "area_weighted_balance_error_z": float(weighted["area_weighted_balance"][2]),
            "scalar_vs_directional_impulse_error_x": float(abs(scalar_vs_directional_impulse_error[0])),
            "scalar_vs_directional_impulse_error_y": float(abs(scalar_vs_directional_impulse_error[1])),
            "scalar_vs_directional_impulse_error_z": float(abs(scalar_vs_directional_impulse_error[2])),
            "scalar_vs_directional_impulse_error_norm": float(np.linalg.norm(scalar_vs_directional_impulse_error)),
            "scalar_vs_directional_solid_error_x": float(abs(scalar_vs_directional_solid_error[0])),
            "scalar_vs_directional_solid_error_norm": float(np.linalg.norm(scalar_vs_directional_solid_error)),
            "hydro_force_sum_x": float(hydro_sum[0]),
            "hydro_force_sum_y": float(hydro_sum[1]),
            "hydro_force_sum_z": float(hydro_sum[2]),
            "hydro_vs_directional_solid_error_x": float(abs(hydro_vs_directional_solid_error[0])),
            "hydro_vs_directional_solid_error_norm": float(np.linalg.norm(hydro_vs_directional_solid_error)),
            "correction_abs_sum": float(np.sum(directional["correction_abs_sum_by_dir"])),
            "correction_abs_max": float(np.max(directional["correction_abs_max_by_dir"])),
        }

    @staticmethod
    def save_directional_npz(lbm, path):
        directional = LinkAreaMomentumAccounting3D.read_directional_stats(lbm)
        metadata = LinkAreaMomentumAccounting3D.direction_metadata(lbm)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(
            path,
            e=metadata["e"],
            length=metadata["length"],
            direction_class=metadata["direction_class"].astype(str),
            link_count_by_dir=directional["link_count_by_dir"],
            fluid_impulse_by_dir=directional["fluid_impulse_by_dir"],
            solid_force_by_dir=directional["solid_force_by_dir"],
            correction_abs_sum_by_dir=directional["correction_abs_sum_by_dir"],
            correction_abs_max_by_dir=directional["correction_abs_max_by_dir"],
        )
