import taichi as ti
import numpy as np
try:
    from pyevtk.hl import gridToVTK
except ModuleNotFoundError:
    gridToVTK = None

from .config import LBMConfig
from .relaxation_semantics import tau_from_legacy_external_solver_parameter
from .relaxation_semantics import (
    LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
    STANDARD_LATTICE_KINEMATIC_VISCOSITY,
    tau_from_lattice_kinematic_viscosity,
)

EQUILIBRIUM_ALL_POPULATION_RESET = "equilibrium_all_population_reset"
REGULARIZED_VELOCITY_PRESSURE = "regularized_velocity_pressure"
REGULARIZED_VELOCITY_PRESSURE_LIMITED = "regularized_velocity_pressure_limited"
CONVECTIVE_PRESSURE_OUTLET_EXPERIMENTAL = "convective_pressure_outlet_experimental"
REGULARIZED_MASS_BALANCED_PRESSURE_OUTLET = "regularized_mass_balanced_pressure_outlet"
CONVECTIVE_MASS_BALANCED_PRESSURE_OUTLET = "convective_mass_balanced_pressure_outlet"
REGULARIZED_FLUX_MATCHED_PRESSURE_OUTLET = "regularized_flux_matched_pressure_outlet"
CONVECTIVE_FLUX_MATCHED_DAMPED_OUTLET = "convective_flux_matched_damped_outlet"
REGULARIZED_PLANE_FLUX_CONTROLLED_PRESSURE_OUTLET = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE_FLUX_CONTROLLED_DAMPED_OUTLET = "convective_plane_flux_controlled_damped_outlet"
UNKNOWN_X_MIN_POPULATIONS = (1, 7, 9, 11, 13)
UNKNOWN_X_MAX_POPULATIONS = (2, 8, 10, 12, 14)

#ti.init(arch=ti.gpu, dynamic_index=False, kernel_profiler=True, print_ir=False)

@ti.data_oriented
class LBMFluid3D:
    def __init__(self, config: LBMConfig):
        if config.sparse_storage:
            raise NotImplementedError(
                "Step 2 only supports dense storage. Enable sparse storage after FSI coupling is validated."
            )

        self.enable_projection = True
        self.config = config
        self.sparse_storage = False
        nx, ny, nz = config.nx, config.ny, config.nz
        self.nx,self.ny,self.nz = nx,ny,nz
        #nx,ny,nz = 120,120,120
        self.fx,self.fy,self.fz = config.force
        self.niu = config.niu
        self.rho0 = config.rho0
        self.relaxation_semantics = config.relaxation_semantics
        self.open_boundary_semantics = config.open_boundary_semantics
        self.open_boundary_limiter_enabled = bool(config.open_boundary_limiter_enabled)
        self.open_boundary_rho_min = float(config.open_boundary_rho_min)
        self.open_boundary_rho_max = float(config.open_boundary_rho_max)
        self.open_boundary_u_max = float(config.open_boundary_u_max)
        self.open_boundary_noneq_cap = float(config.open_boundary_noneq_cap)
        self.open_boundary_flux_feedback_gain_u = float(config.open_boundary_flux_feedback_gain_u)
        self.open_boundary_flux_feedback_gain_rho = float(config.open_boundary_flux_feedback_gain_rho)
        self.open_boundary_flux_filter_alpha = float(config.open_boundary_flux_filter_alpha)
        self.open_boundary_flux_correction_cap_u = float(config.open_boundary_flux_correction_cap_u)
        self.open_boundary_flux_feedback_delta_cap_u = float(config.open_boundary_flux_feedback_delta_cap_u)
        self.open_boundary_flux_feedback_slew_alpha = float(config.open_boundary_flux_feedback_slew_alpha)
        self.open_boundary_convective_blend_weight = float(config.open_boundary_convective_blend_weight)
        self.open_boundary_flux_control_measure_plane_offset = int(config.open_boundary_flux_control_measure_plane_offset)
        self.open_boundary_flux_control_target_scale = float(config.open_boundary_flux_control_target_scale)
        self.open_boundary_outlet_flux_drop_guard_enabled = bool(config.open_boundary_outlet_flux_drop_guard_enabled)
        self.open_boundary_outlet_flux_drop_guard_min_ratio = float(config.open_boundary_outlet_flux_drop_guard_min_ratio)
        self.open_boundary_population_floor_enabled = config.open_boundary_population_floor is not None
        self.open_boundary_population_floor = float(
            config.open_boundary_population_floor
            if config.open_boundary_population_floor is not None
            else -1.0e30
        )

        self.max_v=ti.field(ti.f32,shape=())
        self.rho_min = ti.field(ti.f32, shape=())
        self.rho_max = ti.field(ti.f32, shape=())
        self.mass_total = ti.field(ti.f32, shape=())
        self.force_norm_max = ti.field(ti.f32, shape=())
        self.rho_min_reduced = ti.field(ti.f32, shape=())
        self.rho_max_reduced = ti.field(ti.f32, shape=())
        self.max_v_reduced = ti.field(ti.f32, shape=())
        self.f_min_reduced = ti.field(ti.f32, shape=())
        self.f_max_reduced = ti.field(ti.f32, shape=())
        self.F_min_reduced = ti.field(ti.f32, shape=())
        self.F_max_reduced = ti.field(ti.f32, shape=())
        self.negative_population_count_reduced = ti.field(ti.i32, shape=())
        self.mass_total_reduced = ti.field(ti.f32, shape=())
        self.fluid_cell_count_reduced = ti.field(ti.i32, shape=())
        self.boundary_x_min_negative_count = ti.field(ti.i32, shape=())
        self.boundary_x_max_negative_count = ti.field(ti.i32, shape=())
        self.population_entry_count_reduced = ti.field(ti.i32, shape=())
        self.ob_rho_clip_count_step = ti.field(ti.i32, shape=())
        self.ob_rho_clip_count_run = ti.field(ti.i32, shape=())
        self.ob_velocity_clip_count_step = ti.field(ti.i32, shape=())
        self.ob_velocity_clip_count_run = ti.field(ti.i32, shape=())
        self.ob_noneq_clip_count_step = ti.field(ti.i32, shape=())
        self.ob_noneq_clip_count_run = ti.field(ti.i32, shape=())
        self.ob_population_floor_count_step = ti.field(ti.i32, shape=())
        self.ob_population_floor_count_run = ti.field(ti.i32, shape=())
        self.ob_reconstructed_population_count_step = ti.field(ti.i32, shape=())
        self.ob_reconstructed_population_count_run = ti.field(ti.i32, shape=())
        self.ob_mass_balance_correction_count_step = ti.field(ti.i32, shape=())
        self.ob_mass_balance_correction_count_run = ti.field(ti.i32, shape=())
        self.ob_mass_balance_correction_abs_sum_step = ti.field(ti.f32, shape=())
        self.ob_mass_balance_correction_abs_sum_run = ti.field(ti.f32, shape=())
        self.ob_unknown_population_delta_abs_sum_step = ti.field(ti.f32, shape=())
        self.ob_unknown_population_delta_abs_sum_run = ti.field(ti.f32, shape=())
        self.ob_flow_correction_delta_abs_sum_step = ti.field(ti.f32, shape=())
        self.ob_flow_correction_delta_abs_sum_run = ti.field(ti.f32, shape=())
        self.ob_flow_outlet_flux_error_filtered_run = ti.field(ti.f32, shape=())
        self.ob_flow_correction_gain_effective_step = ti.field(ti.f32, shape=())
        self.ob_target_outlet_flux = ti.field(ti.f32, shape=())
        self.ob_measured_outlet_flux = ti.field(ti.f32, shape=())
        self.ob_flux_error_filtered = ti.field(ti.f32, shape=())
        self.ob_outlet_fluid_area = ti.field(ti.f32, shape=())
        self.ob_flux_control_u_feedback = ti.field(ti.f32, shape=())
        self.ob_flux_control_rho_feedback = ti.field(ti.f32, shape=())
        self.ob_flux_control_saturation_count_step = ti.field(ti.i32, shape=())
        self.ob_flux_control_saturation_count_run = ti.field(ti.i32, shape=())
        self.ob_flux_control_update_count_step = ti.field(ti.i32, shape=())
        self.ob_flux_control_update_count_run = ti.field(ti.i32, shape=())
        self.ob_near_outlet_flux_xminus1 = ti.field(ti.f32, shape=())
        self.ob_near_outlet_flux_xminus2 = ti.field(ti.f32, shape=())
        self.ob_near_outlet_flux_xminus3 = ti.field(ti.f32, shape=())
        self.ob_true_outlet_flux_for_guard = ti.field(ti.f32, shape=())
        self.ob_drop_guard_active_step = ti.field(ti.i32, shape=())
        self.ob_drop_guard_activation_count_run = ti.field(ti.i32, shape=())
        self.ob_drop_guard_reference_flux = ti.field(ti.f32, shape=())

        #Boundary condition mode: 0=periodic, 1= fix pressure, 2=fix velocity; boundary pressure value (rho); boundary velocity value for vx,vy,vz
        self.bc_x_left, self.rho_bcxl, self.vx_bcxl, self.vy_bcxl, self.vz_bcxl = (
            config.bc_x_left,
            config.rho_bc_x_left,
            config.vel_bc_x_left[0],
            config.vel_bc_x_left[1],
            config.vel_bc_x_left[2],
        )
        self.bc_x_right, self.rho_bcxr, self.vx_bcxr, self.vy_bcxr, self.vz_bcxr = (
            config.bc_x_right,
            config.rho_bc_x_right,
            config.vel_bc_x_right[0],
            config.vel_bc_x_right[1],
            config.vel_bc_x_right[2],
        )
        self.bc_y_left, self.rho_bcyl, self.vx_bcyl, self.vy_bcyl, self.vz_bcyl = (
            config.bc_y_left,
            config.rho_bc_y_left,
            config.vel_bc_y_left[0],
            config.vel_bc_y_left[1],
            config.vel_bc_y_left[2],
        )
        self.bc_y_right, self.rho_bcyr, self.vx_bcyr, self.vy_bcyr, self.vz_bcyr = (
            config.bc_y_right,
            config.rho_bc_y_right,
            config.vel_bc_y_right[0],
            config.vel_bc_y_right[1],
            config.vel_bc_y_right[2],
        )
        self.bc_z_left, self.rho_bczl, self.vx_bczl, self.vy_bczl, self.vz_bczl = (
            config.bc_z_left,
            config.rho_bc_z_left,
            config.vel_bc_z_left[0],
            config.vel_bc_z_left[1],
            config.vel_bc_z_left[2],
        )
        self.bc_z_right, self.rho_bczr, self.vx_bczr, self.vy_bczr, self.vz_bczr = (
            config.bc_z_right,
            config.rho_bc_z_right,
            config.vel_bc_z_right[0],
            config.vel_bc_z_right[1],
            config.vel_bc_z_right[2],
        )

        self.f = ti.Vector.field(19,ti.f32,shape=(nx,ny,nz))
        self.F = ti.Vector.field(19,ti.f32,shape=(nx,ny,nz))
        self.rho = ti.field(ti.f32, shape=(nx,ny,nz))
        self.v = ti.Vector.field(3,ti.f32, shape=(nx,ny,nz))



        self.e = ti.Vector.field(3,ti.i32, shape=(19))
        self.S_dig = ti.Vector.field(19,ti.f32,shape=())
        self.e_f = ti.Vector.field(3,ti.f32, shape=(19))
        self.w = ti.field(ti.f32, shape=(19))
        self.solid = ti.field(ti.i8,shape=(nx,ny,nz))
        self.static_solid = ti.field(ti.i8, shape=(nx,ny,nz))
        self.old_solid = ti.field(ti.i8, shape=(nx,ny,nz))
        self.solid_phi = ti.field(ti.f32, shape=(nx,ny,nz))
        self.solid_mass = ti.field(ti.f32, shape=(nx,ny,nz))
        self.solid_vel = ti.Vector.field(3, ti.f32, shape=(nx,ny,nz))
        self.cell_force = ti.Vector.field(3, ti.f32, shape=(nx,ny,nz))
        self.hydro_force = ti.Vector.field(3, ti.f32, shape=(nx,ny,nz))
        self.hydro_force_accum = ti.Vector.field(3, ti.f32, shape=(nx,ny,nz))
        self.mb_subcycle_force_sample_count = ti.field(ti.i32, shape=())
        self.mb_subcycle_force_accum_norm_max = ti.field(ti.f32, shape=())
        self.mb_subcycle_force_mean_norm_max = ti.field(ti.f32, shape=())
        self.bb_link_count = ti.field(ti.i32, shape=())
        self.bb_max_correction = ti.field(ti.f32, shape=())
        self.bb_net_fluid_impulse = ti.Vector.field(3, ti.f32, shape=())
        self.bb_net_solid_force = ti.Vector.field(3, ti.f32, shape=())
        self.bb_link_count_by_dir = ti.field(ti.i32, shape=(19,))
        self.bb_fluid_impulse_by_dir = ti.Vector.field(3, ti.f32, shape=(19,))
        self.bb_solid_force_by_dir = ti.Vector.field(3, ti.f32, shape=(19,))
        self.bb_correction_abs_sum_by_dir = ti.field(ti.f32, shape=(19,))
        self.bb_correction_abs_max_by_dir = ti.field(ti.f32, shape=(19,))
        self.reinit_flag = ti.field(ti.i8, shape=(nx,ny,nz))
        self.ext_f = ti.Vector.field(3,ti.f32,shape=())


        self.M = ti.Matrix.field(19, 19, ti.f32, shape=())
        self.inv_M = ti.Matrix.field(19,19,ti.f32, shape=())

        M_np = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [-1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,-2,-2,-2,-2,-2,-2,1,1,1,1,1,1,1,1,1,1,1,1],
        [0,1,-1,0,0,0,0,1,-1,1,-1,1,-1,1,-1,0,0,0,0],
        [0,-2,2,0,0,0,0,1,-1,1,-1,1,-1,1,-1,0,0,0,0],
        [0,0,0,1,-1,0,0,1,-1,-1,1,0,0,0,0,1,-1,1,-1],
        [0,0,0,-2,2,0,0,1,-1,-1,1,0,0,0,0,1,-1,1,-1],
        [0,0,0,0,0,1,-1,0,0,0,0,1,-1,-1,1,1,-1,-1,1],
        [0,0,0,0,0,-2,2,0,0,0,0,1,-1,-1,1,1,-1,-1,1],
        [0,2,2,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-2,-2,-2,-2],
        [0,-2,-2,1,1,1,1,1,1,1,1,1,1,1,1,-2,-2,-2,-2],
        [0,0,0,1,1,-1,-1,1,1,1,1,-1,-1,-1,-1,0,0,0,0],
        [0,0,0,-1,-1,1,1,1,1,1,1,-1,-1,-1,-1,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,-1,-1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,-1,-1],
        [0,0,0,0,0,0,0,0,0,0,0,1,1,-1,-1,0,0,0,0],
        [0,0,0,0,0,0,0,1,-1,1,-1,-1,1,-1,1,0,0,0,0],
        [0,0,0,0,0,0,0,-1,1,1,-1,0,0,0,0,1,-1,1,-1],
        [0,0,0,0,0,0,0,0,0,0,0,1,-1,-1,1,-1,1,1,-1]])
        inv_M_np = np.linalg.inv(M_np)

        self.LR = [0,2,1,4,3,6,5,8,7,10,9,12,11,14,13,16,15,18,17]




        self.M[None] = ti.Matrix([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [-1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,-2,-2,-2,-2,-2,-2,1,1,1,1,1,1,1,1,1,1,1,1],
        [0,1,-1,0,0,0,0,1,-1,1,-1,1,-1,1,-1,0,0,0,0],
        [0,-2,2,0,0,0,0,1,-1,1,-1,1,-1,1,-1,0,0,0,0],
        [0,0,0,1,-1,0,0,1,-1,-1,1,0,0,0,0,1,-1,1,-1],
        [0,0,0,-2,2,0,0,1,-1,-1,1,0,0,0,0,1,-1,1,-1],
        [0,0,0,0,0,1,-1,0,0,0,0,1,-1,-1,1,1,-1,-1,1],
        [0,0,0,0,0,-2,2,0,0,0,0,1,-1,-1,1,1,-1,-1,1],
        [0,2,2,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-2,-2,-2,-2],
        [0,-2,-2,1,1,1,1,1,1,1,1,1,1,1,1,-2,-2,-2,-2],
        [0,0,0,1,1,-1,-1,1,1,1,1,-1,-1,-1,-1,0,0,0,0],
        [0,0,0,-1,-1,1,1,1,1,1,1,-1,-1,-1,-1,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,-1,-1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,-1,-1],
        [0,0,0,0,0,0,0,0,0,0,0,1,1,-1,-1,0,0,0,0],
        [0,0,0,0,0,0,0,1,-1,1,-1,-1,1,-1,1,0,0,0,0],
        [0,0,0,0,0,0,0,-1,1,1,-1,0,0,0,0,1,-1,1,-1],
        [0,0,0,0,0,0,0,0,0,0,0,1,-1,-1,1,-1,1,1,-1]])

        self.inv_M[None] = ti.Matrix(inv_M_np)

        self.x = np.linspace(0, nx, nx)
        self.y = np.linspace(0, ny, ny)
        self.z = np.linspace(0, nz, nz)
        #X, Y, Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')


    def init_simulation(self):
        self.bc_vel_x_left = [self.vx_bcxl, self.vy_bcxl, self.vz_bcxl]
        self.bc_vel_x_left_dynamic = ti.Vector.field(3, ti.f32, shape=())
        self.bc_vel_x_left_dynamic[None] = self.bc_vel_x_left
        self.bc_vel_x_right = [self.vx_bcxr, self.vy_bcxr, self.vz_bcxr]
        self.bc_vel_y_left = [self.vx_bcyl, self.vy_bcyl, self.vz_bcyl]
        self.bc_vel_y_right = [self.vx_bcyr, self.vy_bcyr, self.vz_bcyr]
        self.bc_vel_z_left = [self.vx_bczl, self.vy_bczl, self.vz_bczl]
        self.bc_vel_z_right = [self.vx_bczr, self.vy_bczr, self.vz_bczr]

        if self.relaxation_semantics == STANDARD_LATTICE_KINEMATIC_VISCOSITY:
            self.tau_f = tau_from_lattice_kinematic_viscosity(self.niu)
        elif self.relaxation_semantics == LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER:
            self.tau_f = tau_from_legacy_external_solver_parameter(self.niu)
        else:
            raise ValueError(f"unsupported LBM relaxation semantics: {self.relaxation_semantics}")
        self.s_v=1.0/self.tau_f
        self.s_other=8.0*(2.0-self.s_v)/(8.0-self.s_v)

        self.S_dig[None] = ti.Vector([0,self.s_v,self.s_v,0,self.s_other,0,self.s_other,0,self.s_other, self.s_v, self.s_v,self.s_v,self.s_v,self.s_v,self.s_v,self.s_v,self.s_other,self.s_other,self.s_other])

        #self.ext_f[None] = ti.Vector([self.fx,self.fy,self.fz])
        self.ext_f[None][0] = self.fx
        self.ext_f[None][1] = self.fy
        self.ext_f[None][2] = self.fz

        ti.static(self.inv_M)
        ti.static(self.M)
        #ti.static(LR)
        ti.static(self.S_dig)

        self.static_init()
        self.init()


    @ti.func
    def feq(self, k,rho_local, u):
        eu = self.e[k].dot(u)
        uv = u.dot(u)
        feqout = self.w[k]*rho_local*(1.0+3.0*eu+4.5*eu*eu-1.5*uv)
        #print(k, rho_local, self.w[k])
        return feqout

    @ti.kernel
    def init(self):
        for i,j,k in self.solid:
            #print(i,j,k)
            if (self.solid[i,j,k]==0):
                self.rho[i,j,k] = self.rho0
                self.v[i,j,k] = ti.Vector([0,0,0])
                for s in ti.static(range(19)):
                    self.f[i,j,k][s] = self.feq(s,self.rho0,self.v[i,j,k])
                    self.F[i,j,k][s] = self.feq(s,self.rho0,self.v[i,j,k])
                    #print(F[i,j,k,s], feq(s,1.0,v[i,j,k]))
            else:
                self.rho[i,j,k] = self.rho0
                self.v[i,j,k] = ti.Vector([0,0,0])
                for s in ti.static(range(19)):
                    self.f[i,j,k][s] = self.feq(s,self.rho0,self.v[i,j,k])
                    self.F[i,j,k][s] = self.feq(s,self.rho0,self.v[i,j,k])


    def init_geo(self,filename):
        in_dat = np.loadtxt(filename)
        in_dat[in_dat>0] = 1
        in_dat = np.reshape(in_dat, (self.nx,self.ny,self.nz),order='F')
        in_dat = in_dat.astype(np.int8)
        self.solid.from_numpy(in_dat)
        self.copy_solid_to_static()


    @ti.kernel
    def static_init(self):
        if ti.static(self.enable_projection): # No runtime overhead
            self.e[0] = ti.Vector([0,0,0])
            self.e[1] = ti.Vector([1,0,0]); self.e[2] = ti.Vector([-1,0,0]); self.e[3] = ti.Vector([0,1,0]); self.e[4] = ti.Vector([0,-1,0]);self.e[5] = ti.Vector([0,0,1]); self.e[6] = ti.Vector([0,0,-1])
            self.e[7] = ti.Vector([1,1,0]); self.e[8] = ti.Vector([-1,-1,0]); self.e[9] = ti.Vector([1,-1,0]); self.e[10] = ti.Vector([-1,1,0])
            self.e[11] = ti.Vector([1,0,1]); self.e[12] = ti.Vector([-1,0,-1]); self.e[13] = ti.Vector([1,0,-1]); self.e[14] = ti.Vector([-1,0,1])
            self.e[15] = ti.Vector([0,1,1]); self.e[16] = ti.Vector([0,-1,-1]); self.e[17] = ti.Vector([0,1,-1]); self.e[18] = ti.Vector([0,-1,1])

            self.e_f[0] = ti.Vector([0,0,0])
            self.e_f[1] = ti.Vector([1,0,0]); self.e_f[2] = ti.Vector([-1,0,0]); self.e_f[3] = ti.Vector([0,1,0]); self.e_f[4] = ti.Vector([0,-1,0]);self.e_f[5] = ti.Vector([0,0,1]); self.e_f[6] = ti.Vector([0,0,-1])
            self.e_f[7] = ti.Vector([1,1,0]); self.e_f[8] = ti.Vector([-1,-1,0]); self.e_f[9] = ti.Vector([1,-1,0]); self.e_f[10] = ti.Vector([-1,1,0])
            self.e_f[11] = ti.Vector([1,0,1]); self.e_f[12] = ti.Vector([-1,0,-1]); self.e_f[13] = ti.Vector([1,0,-1]); self.e_f[14] = ti.Vector([-1,0,1])
            self.e_f[15] = ti.Vector([0,1,1]); self.e_f[16] = ti.Vector([0,-1,-1]); self.e_f[17] = ti.Vector([0,1,-1]); self.e_f[18] = ti.Vector([0,-1,1])

            self.w[0] = 1.0/3.0; self.w[1] = 1.0/18.0; self.w[2] = 1.0/18.0; self.w[3] = 1.0/18.0; self.w[4] = 1.0/18.0; self.w[5] = 1.0/18.0; self.w[6] = 1.0/18.0;
            self.w[7] = 1.0/36.0; self.w[8] = 1.0/36.0; self.w[9] = 1.0/36.0; self.w[10] = 1.0/36.0; self.w[11] = 1.0/36.0; self.w[12] = 1.0/36.0;
            self.w[13] = 1.0/36.0; self.w[14] = 1.0/36.0; self.w[15] = 1.0/36.0; self.w[16] = 1.0/36.0; self.w[17] = 1.0/36.0; self.w[18] = 1.0/36.0;


    #@ti.func
    #def GuoF(self,i,j,k,s,u,f):
    #    out=0.0
    #    for l in ti.static(range(19)):
    #        out += self.w[l]*((self.e_f[l]-u).dot(f)+(self.e_f[l].dot(u)*(self.e_f[l].dot(f))))*self.M[None][s,l]
    #
    #    return out


    @ti.func
    def meq_vec(self, rho_local,u):
        out = ti.Vector([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        out[0] = rho_local;             out[3] = u[0];    out[5] = u[1];    out[7] = u[2];
        out[1] = u.dot(u);    out[9] = 2*u.x*u.x-u.y*u.y-u.z*u.z;         out[11] = u.y*u.y-u.z*u.z
        out[13] = u.x*u.y;    out[14] = u.y*u.z;                            out[15] = u.x*u.z
        return out

    @ti.func
    def cal_local_force(self,i,j,k):
        f = ti.Vector([self.fx, self.fy, self.fz]) + self.cell_force[i,j,k]
        return f

    @ti.kernel
    def colission(self):
        for i,j,k in self.rho:
            if (self.solid[i,j,k] == 0 and i<self.nx and j<self.ny and k<self.nz):
                m_temp = self.M[None]@self.F[i,j,k]
                meq = self.meq_vec(self.rho[i,j,k],self.v[i,j,k])
                m_temp -= self.S_dig[None]*(m_temp-meq)
                f = self.cal_local_force(i,j,k)
                guo_dist = ti.Vector([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                for l in ti.static(range(19)):
                    guo_dist[l] = self.w[l]*((self.e_f[l]-self.v[i,j,k]).dot(f)/3.0+(self.e_f[l].dot(self.v[i,j,k])*(self.e_f[l].dot(f)))/9.0)
                guo_moment = self.M[None]@guo_dist
                m_temp += (1.0-0.5*self.S_dig[None])*guo_moment

                self.f[i,j,k] = ti.Vector([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                self.f[i,j,k] += self.inv_M[None]@m_temp





    @ti.func
    def periodic_index(self,i):
        iout = i
        if i[0]<0:     iout[0] = self.nx-1
        if i[0]>self.nx-1:  iout[0] = 0
        if i[1]<0:     iout[1] = self.ny-1
        if i[1]>self.ny-1:  iout[1] = 0
        if i[2]<0:     iout[2] = self.nz-1
        if i[2]>self.nz-1:  iout[2] = 0

        return iout

    @ti.kernel
    def streaming1(self):
        for i in ti.grouped(self.rho):
            if (self.solid[i] == 0 and i.x<self.nx and i.y<self.ny and i.z<self.nz):
                for s in ti.static(range(19)):
                    ip = self.periodic_index(i+self.e[s])
                    if (self.solid[ip]==0):
                        self.F[ip][s] = self.f[i][s]
                    else:
                        self.F[i][self.LR[s]] = self.f[i][s]
                        #print(i, ip, "@@@")

    @ti.kernel
    def clear_moving_boundary_diagnostics(self):
        self.bb_link_count[None] = 0
        self.bb_max_correction[None] = 0.0
        self.bb_net_fluid_impulse[None] = ti.Vector([0.0, 0.0, 0.0])
        self.bb_net_solid_force[None] = ti.Vector([0.0, 0.0, 0.0])

        for s in range(19):
            self.bb_link_count_by_dir[s] = 0
            self.bb_fluid_impulse_by_dir[s] = ti.Vector([0.0, 0.0, 0.0])
            self.bb_solid_force_by_dir[s] = ti.Vector([0.0, 0.0, 0.0])
            self.bb_correction_abs_sum_by_dir[s] = 0.0
            self.bb_correction_abs_max_by_dir[s] = 0.0

        for I in ti.grouped(self.rho):
            self.hydro_force[I] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def clear_moving_boundary_force_accumulator(self):
        self.mb_subcycle_force_sample_count[None] = 0
        self.mb_subcycle_force_accum_norm_max[None] = 0.0
        self.mb_subcycle_force_mean_norm_max[None] = 0.0
        for I in ti.grouped(self.rho):
            self.hydro_force_accum[I] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def accumulate_moving_boundary_force_sample(self):
        self.mb_subcycle_force_sample_count[None] += 1
        for I in ti.grouped(self.rho):
            self.hydro_force_accum[I] += self.hydro_force[I]
            ti.atomic_max(self.mb_subcycle_force_accum_norm_max[None], self.hydro_force_accum[I].norm())

    @ti.kernel
    def finalize_moving_boundary_force_accumulator(self):
        self.mb_subcycle_force_mean_norm_max[None] = 0.0
        sample_count = self.mb_subcycle_force_sample_count[None]
        inv_count = 0.0
        if sample_count > 0:
            inv_count = 1.0 / ti.cast(sample_count, ti.f32)
        for I in ti.grouped(self.rho):
            if sample_count > 0:
                mean_force = self.hydro_force_accum[I] * inv_count
                self.hydro_force[I] = mean_force
                ti.atomic_max(self.mb_subcycle_force_mean_norm_max[None], mean_force.norm())

    @ti.kernel
    def streaming_moving_bounceback(self):
        for i in ti.grouped(self.rho):
            if (self.solid[i] == 0 and i.x<self.nx and i.y<self.ny and i.z<self.nz):
                for s in ti.static(range(19)):
                    ip = self.periodic_index(i+self.e[s])
                    if (self.solid[ip]==0):
                        self.F[ip][s] = self.f[i][s]
                    else:
                        rho_local = self.rho[i]
                        u_wall = self.solid_vel[ip]
                        correction = -6.0 * self.w[s] * rho_local * self.e_f[s].dot(u_wall)
                        bounced = self.f[i][s] + correction
                        self.F[i][self.LR[s]] = bounced

                        incoming_momentum = self.e_f[s] * self.f[i][s]
                        outgoing_momentum = self.e_f[self.LR[s]] * bounced
                        fluid_impulse = outgoing_momentum - incoming_momentum
                        solid_force = -fluid_impulse

                        ti.atomic_add(self.bb_link_count[None], 1)
                        ti.atomic_max(self.bb_max_correction[None], ti.abs(correction))
                        ti.atomic_add(self.bb_link_count_by_dir[s], 1)
                        ti.atomic_add(self.bb_correction_abs_sum_by_dir[s], ti.abs(correction))
                        ti.atomic_max(self.bb_correction_abs_max_by_dir[s], ti.abs(correction))

                        for d in ti.static(range(3)):
                            ti.atomic_add(self.bb_net_fluid_impulse[None][d], fluid_impulse[d])
                            ti.atomic_add(self.bb_net_solid_force[None][d], solid_force[d])
                            ti.atomic_add(self.hydro_force[ip][d], solid_force[d])
                            ti.atomic_add(self.bb_fluid_impulse_by_dir[s][d], fluid_impulse[d])
                            ti.atomic_add(self.bb_solid_force_by_dir[s][d], solid_force[d])

    @ti.kernel
    def finalize_moving_boundary_diagnostics(self):
        link_count = 0
        fluid_impulse = ti.Vector([0.0, 0.0, 0.0])
        solid_force = ti.Vector([0.0, 0.0, 0.0])
        max_correction = 0.0
        for s in ti.static(range(19)):
            link_count += self.bb_link_count_by_dir[s]
            fluid_impulse += self.bb_fluid_impulse_by_dir[s]
            solid_force += self.bb_solid_force_by_dir[s]
            max_correction = ti.max(max_correction, self.bb_correction_abs_max_by_dir[s])

        self.bb_link_count[None] = link_count
        self.bb_max_correction[None] = max_correction
        self.bb_net_fluid_impulse[None] = fluid_impulse
        self.bb_net_solid_force[None] = solid_force

    def Boundary_condition(self):
        self.clear_open_boundary_limiter_step_counters()
        if self.open_boundary_semantics == REGULARIZED_VELOCITY_PRESSURE:
            self.apply_regularized_x_open_boundaries()
            return
        if self.open_boundary_semantics == REGULARIZED_VELOCITY_PRESSURE_LIMITED:
            self.apply_regularized_limited_x_open_boundaries()
            return
        if self.open_boundary_semantics == CONVECTIVE_PRESSURE_OUTLET_EXPERIMENTAL:
            self.apply_convective_pressure_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == REGULARIZED_MASS_BALANCED_PRESSURE_OUTLET:
            self.apply_regularized_mass_balanced_pressure_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == CONVECTIVE_MASS_BALANCED_PRESSURE_OUTLET:
            self.apply_convective_mass_balanced_pressure_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == REGULARIZED_FLUX_MATCHED_PRESSURE_OUTLET:
            self.apply_regularized_flux_matched_pressure_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == CONVECTIVE_FLUX_MATCHED_DAMPED_OUTLET:
            self.apply_convective_flux_matched_damped_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == REGULARIZED_PLANE_FLUX_CONTROLLED_PRESSURE_OUTLET:
            self.update_open_boundary_plane_flux_controller()
            self.apply_regularized_plane_flux_controlled_pressure_outlet_x_open_boundaries()
            return
        if self.open_boundary_semantics == CONVECTIVE_PLANE_FLUX_CONTROLLED_DAMPED_OUTLET:
            self.update_open_boundary_plane_flux_controller()
            self.apply_convective_plane_flux_controlled_damped_outlet_x_open_boundaries()
            return
        self.Boundary_condition_legacy()

    @ti.kernel
    def clear_open_boundary_limiter_step_counters(self):
        self.ob_rho_clip_count_step[None] = 0
        self.ob_velocity_clip_count_step[None] = 0
        self.ob_noneq_clip_count_step[None] = 0
        self.ob_population_floor_count_step[None] = 0
        self.ob_reconstructed_population_count_step[None] = 0
        self.ob_mass_balance_correction_count_step[None] = 0
        self.ob_mass_balance_correction_abs_sum_step[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_step[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_step[None] = 0.0
        self.ob_flow_correction_gain_effective_step[None] = 0.0
        self.ob_flux_control_saturation_count_step[None] = 0
        self.ob_flux_control_update_count_step[None] = 0
        self.ob_drop_guard_active_step[None] = 0

    @ti.kernel
    def clear_open_boundary_limiter_run_counters(self):
        self.ob_rho_clip_count_step[None] = 0
        self.ob_rho_clip_count_run[None] = 0
        self.ob_velocity_clip_count_step[None] = 0
        self.ob_velocity_clip_count_run[None] = 0
        self.ob_noneq_clip_count_step[None] = 0
        self.ob_noneq_clip_count_run[None] = 0
        self.ob_population_floor_count_step[None] = 0
        self.ob_population_floor_count_run[None] = 0
        self.ob_reconstructed_population_count_step[None] = 0
        self.ob_reconstructed_population_count_run[None] = 0
        self.ob_mass_balance_correction_count_step[None] = 0
        self.ob_mass_balance_correction_count_run[None] = 0
        self.ob_mass_balance_correction_abs_sum_step[None] = 0.0
        self.ob_mass_balance_correction_abs_sum_run[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_step[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_run[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_step[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_run[None] = 0.0
        self.ob_flow_outlet_flux_error_filtered_run[None] = 0.0
        self.ob_flow_correction_gain_effective_step[None] = 0.0
        self.ob_target_outlet_flux[None] = 0.0
        self.ob_measured_outlet_flux[None] = 0.0
        self.ob_flux_error_filtered[None] = 0.0
        self.ob_outlet_fluid_area[None] = 0.0
        self.ob_flux_control_u_feedback[None] = 0.0
        self.ob_flux_control_rho_feedback[None] = 0.0
        self.ob_flux_control_saturation_count_step[None] = 0
        self.ob_flux_control_saturation_count_run[None] = 0
        self.ob_flux_control_update_count_step[None] = 0
        self.ob_flux_control_update_count_run[None] = 0
        self.ob_near_outlet_flux_xminus1[None] = 0.0
        self.ob_near_outlet_flux_xminus2[None] = 0.0
        self.ob_near_outlet_flux_xminus3[None] = 0.0
        self.ob_true_outlet_flux_for_guard[None] = 0.0
        self.ob_drop_guard_active_step[None] = 0
        self.ob_drop_guard_activation_count_run[None] = 0
        self.ob_drop_guard_reference_flux[None] = 0.0

    @ti.kernel
    def set_open_boundary_limiter_run_counters(
        self,
        rho_clip_count: ti.i32,
        velocity_clip_count: ti.i32,
        noneq_clip_count: ti.i32,
        population_floor_count: ti.i32,
        reconstructed_population_count: ti.i32,
    ):
        self.ob_rho_clip_count_step[None] = 0
        self.ob_rho_clip_count_run[None] = rho_clip_count
        self.ob_velocity_clip_count_step[None] = 0
        self.ob_velocity_clip_count_run[None] = velocity_clip_count
        self.ob_noneq_clip_count_step[None] = 0
        self.ob_noneq_clip_count_run[None] = noneq_clip_count
        self.ob_population_floor_count_step[None] = 0
        self.ob_population_floor_count_run[None] = population_floor_count
        self.ob_reconstructed_population_count_step[None] = 0
        self.ob_reconstructed_population_count_run[None] = reconstructed_population_count
        self.ob_mass_balance_correction_count_step[None] = 0
        self.ob_mass_balance_correction_count_run[None] = 0
        self.ob_mass_balance_correction_abs_sum_step[None] = 0.0
        self.ob_mass_balance_correction_abs_sum_run[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_step[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_run[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_step[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_run[None] = 0.0
        self.ob_flow_outlet_flux_error_filtered_run[None] = 0.0
        self.ob_flow_correction_gain_effective_step[None] = 0.0
        self.ob_target_outlet_flux[None] = 0.0
        self.ob_measured_outlet_flux[None] = 0.0
        self.ob_flux_error_filtered[None] = 0.0
        self.ob_outlet_fluid_area[None] = 0.0
        self.ob_flux_control_u_feedback[None] = 0.0
        self.ob_flux_control_rho_feedback[None] = 0.0
        self.ob_flux_control_saturation_count_step[None] = 0
        self.ob_flux_control_saturation_count_run[None] = 0
        self.ob_flux_control_update_count_step[None] = 0
        self.ob_flux_control_update_count_run[None] = 0
        self.ob_near_outlet_flux_xminus1[None] = 0.0
        self.ob_near_outlet_flux_xminus2[None] = 0.0
        self.ob_near_outlet_flux_xminus3[None] = 0.0
        self.ob_true_outlet_flux_for_guard[None] = 0.0
        self.ob_drop_guard_active_step[None] = 0
        self.ob_drop_guard_activation_count_run[None] = 0
        self.ob_drop_guard_reference_flux[None] = 0.0

    @ti.kernel
    def set_open_boundary_repair_run_counters(
        self,
        mass_balance_correction_count: ti.i32,
        mass_balance_correction_abs_sum: ti.f32,
        unknown_population_delta_abs_sum: ti.f32,
    ):
        self.ob_mass_balance_correction_count_step[None] = 0
        self.ob_mass_balance_correction_count_run[None] = mass_balance_correction_count
        self.ob_mass_balance_correction_abs_sum_step[None] = 0.0
        self.ob_mass_balance_correction_abs_sum_run[None] = mass_balance_correction_abs_sum
        self.ob_unknown_population_delta_abs_sum_step[None] = 0.0
        self.ob_unknown_population_delta_abs_sum_run[None] = unknown_population_delta_abs_sum
        self.ob_flow_correction_delta_abs_sum_step[None] = 0.0
        self.ob_flow_correction_delta_abs_sum_run[None] = 0.0
        self.ob_flow_outlet_flux_error_filtered_run[None] = 0.0
        self.ob_flow_correction_gain_effective_step[None] = 0.0
        self.ob_target_outlet_flux[None] = 0.0
        self.ob_measured_outlet_flux[None] = 0.0
        self.ob_flux_error_filtered[None] = 0.0
        self.ob_outlet_fluid_area[None] = 0.0
        self.ob_flux_control_u_feedback[None] = 0.0
        self.ob_flux_control_rho_feedback[None] = 0.0
        self.ob_flux_control_saturation_count_step[None] = 0
        self.ob_flux_control_saturation_count_run[None] = 0
        self.ob_flux_control_update_count_step[None] = 0
        self.ob_flux_control_update_count_run[None] = 0
        self.ob_near_outlet_flux_xminus1[None] = 0.0
        self.ob_near_outlet_flux_xminus2[None] = 0.0
        self.ob_near_outlet_flux_xminus3[None] = 0.0
        self.ob_true_outlet_flux_for_guard[None] = 0.0
        self.ob_drop_guard_active_step[None] = 0
        self.ob_drop_guard_activation_count_run[None] = 0
        self.ob_drop_guard_reference_flux[None] = 0.0

    @ti.kernel
    def reduce_lbm_stability_diagnostics(self):
        self.rho_min_reduced[None] = 1.0e30
        self.rho_max_reduced[None] = -1.0e30
        self.max_v_reduced[None] = 0.0
        self.f_min_reduced[None] = 1.0e30
        self.f_max_reduced[None] = -1.0e30
        self.F_min_reduced[None] = 1.0e30
        self.F_max_reduced[None] = -1.0e30
        self.negative_population_count_reduced[None] = 0
        self.mass_total_reduced[None] = 0.0
        self.fluid_cell_count_reduced[None] = 0
        self.boundary_x_min_negative_count[None] = 0
        self.boundary_x_max_negative_count[None] = 0
        self.population_entry_count_reduced[None] = 0
        for I in ti.grouped(self.rho):
            if self.solid[I] == 0:
                rho_value = self.rho[I]
                ti.atomic_add(self.mass_total_reduced[None], rho_value)
                ti.atomic_add(self.fluid_cell_count_reduced[None], 1)
                ti.atomic_min(self.rho_min_reduced[None], rho_value)
                ti.atomic_max(self.rho_max_reduced[None], rho_value)
                ti.atomic_max(self.max_v_reduced[None], self.v[I].norm())
                for s in ti.static(range(19)):
                    f_value = self.f[I][s]
                    F_value = self.F[I][s]
                    ti.atomic_min(self.f_min_reduced[None], f_value)
                    ti.atomic_max(self.f_max_reduced[None], f_value)
                    ti.atomic_min(self.F_min_reduced[None], F_value)
                    ti.atomic_max(self.F_max_reduced[None], F_value)
                    ti.atomic_add(self.population_entry_count_reduced[None], 2)
                    if f_value < 0.0:
                        ti.atomic_add(self.negative_population_count_reduced[None], 1)
                        if I.x == 0:
                            ti.atomic_add(self.boundary_x_min_negative_count[None], 1)
                        if I.x == self.nx - 1:
                            ti.atomic_add(self.boundary_x_max_negative_count[None], 1)
                    if F_value < 0.0:
                        ti.atomic_add(self.negative_population_count_reduced[None], 1)
                        if I.x == 0:
                            ti.atomic_add(self.boundary_x_min_negative_count[None], 1)
                        if I.x == self.nx - 1:
                            ti.atomic_add(self.boundary_x_max_negative_count[None], 1)

    def get_lightweight_stability_stats(self):
        self.reduce_lbm_stability_diagnostics()
        entry_count = int(self.population_entry_count_reduced[None])
        negative_count = int(self.negative_population_count_reduced[None])
        return {
            "rho_min": float(self.rho_min_reduced[None]),
            "rho_max": float(self.rho_max_reduced[None]),
            "max_v": float(self.max_v_reduced[None]),
            "mass_total": float(self.mass_total_reduced[None]),
            "fluid_cell_count": int(self.fluid_cell_count_reduced[None]),
            "f_min": float(self.f_min_reduced[None]),
            "f_max": float(self.f_max_reduced[None]),
            "F_min": float(self.F_min_reduced[None]),
            "F_max": float(self.F_max_reduced[None]),
            "negative_population_count": negative_count,
            "negative_population_fraction": float(negative_count / entry_count if entry_count else 0.0),
            "population_entry_count": entry_count,
            "boundary_x_min_negative_population_count": int(self.boundary_x_min_negative_count[None]),
            "boundary_x_max_negative_population_count": int(self.boundary_x_max_negative_count[None]),
            "stability_all_finite": True,
        }

    def get_open_boundary_limiter_stats(self):
        step_activation_count = (
            int(self.ob_rho_clip_count_step[None])
            + int(self.ob_velocity_clip_count_step[None])
            + int(self.ob_noneq_clip_count_step[None])
            + int(self.ob_population_floor_count_step[None])
        )
        run_activation_count = (
            int(self.ob_rho_clip_count_run[None])
            + int(self.ob_velocity_clip_count_run[None])
            + int(self.ob_noneq_clip_count_run[None])
            + int(self.ob_population_floor_count_run[None])
        )
        denominator = int(self.ob_reconstructed_population_count_run[None])
        controller_updates = int(self.ob_flux_control_update_count_run[None])
        controller_saturations = int(self.ob_flux_control_saturation_count_run[None])
        controller_feedback_abs = abs(float(self.ob_flux_control_u_feedback[None]))
        controller_density_feedback_abs = abs(float(self.ob_flux_control_rho_feedback[None]))
        controller_cap_abs = abs(float(self.open_boundary_flux_correction_cap_u))
        return {
            "rho_clip_count_step": int(self.ob_rho_clip_count_step[None]),
            "rho_clip_count_run": int(self.ob_rho_clip_count_run[None]),
            "velocity_clip_count_step": int(self.ob_velocity_clip_count_step[None]),
            "velocity_clip_count_run": int(self.ob_velocity_clip_count_run[None]),
            "noneq_clip_count_step": int(self.ob_noneq_clip_count_step[None]),
            "noneq_clip_count_run": int(self.ob_noneq_clip_count_run[None]),
            "population_floor_count_step": int(self.ob_population_floor_count_step[None]),
            "population_floor_count_run": int(self.ob_population_floor_count_run[None]),
            "reconstructed_population_count_step": int(self.ob_reconstructed_population_count_step[None]),
            "reconstructed_population_count_run": int(self.ob_reconstructed_population_count_run[None]),
            "limiter_activation_count_step": step_activation_count,
            "limiter_activation_count": run_activation_count,
            "limiter_activation_denominator": denominator,
            "limiter_activation_fraction": float(run_activation_count / denominator if denominator else 0.0),
            "mass_balance_correction_count_step": int(self.ob_mass_balance_correction_count_step[None]),
            "mass_balance_correction_count_run": int(self.ob_mass_balance_correction_count_run[None]),
            "mass_balance_correction_abs_sum_step": float(self.ob_mass_balance_correction_abs_sum_step[None]),
            "mass_balance_correction_abs_sum_run": float(self.ob_mass_balance_correction_abs_sum_run[None]),
            "unknown_population_delta_abs_sum_step": float(self.ob_unknown_population_delta_abs_sum_step[None]),
            "unknown_population_delta_abs_sum_run": float(self.ob_unknown_population_delta_abs_sum_run[None]),
            "flow_correction_delta_abs_sum_step": float(self.ob_flow_correction_delta_abs_sum_step[None]),
            "flow_correction_delta_abs_sum_run": float(self.ob_flow_correction_delta_abs_sum_run[None]),
            "flow_outlet_flux_error_filtered_run": float(self.ob_flow_outlet_flux_error_filtered_run[None]),
            "flow_correction_gain_effective_step": float(self.ob_flow_correction_gain_effective_step[None]),
            "flow_feedback_gain_u": float(self.open_boundary_flux_feedback_gain_u),
            "flow_feedback_gain_rho": float(self.open_boundary_flux_feedback_gain_rho),
            "flow_filter_alpha": float(self.open_boundary_flux_filter_alpha),
            "flow_correction_cap_u": float(self.open_boundary_flux_correction_cap_u),
            "flow_feedback_delta_cap_u": float(self.open_boundary_flux_feedback_delta_cap_u),
            "flow_feedback_slew_alpha": float(self.open_boundary_flux_feedback_slew_alpha),
            "flow_convective_blend_weight": float(self.open_boundary_convective_blend_weight),
            "flow_control_measure_plane_offset": int(self.open_boundary_flux_control_measure_plane_offset),
            "flow_control_target_scale": float(self.open_boundary_flux_control_target_scale),
            "flow_outlet_flux_drop_guard_enabled": bool(self.open_boundary_outlet_flux_drop_guard_enabled),
            "flow_outlet_flux_drop_guard_min_ratio": float(self.open_boundary_outlet_flux_drop_guard_min_ratio),
            "near_outlet_flux_xminus1": float(self.ob_near_outlet_flux_xminus1[None]),
            "near_outlet_flux_xminus2": float(self.ob_near_outlet_flux_xminus2[None]),
            "near_outlet_flux_xminus3": float(self.ob_near_outlet_flux_xminus3[None]),
            "controller_true_outlet_flux_for_guard": float(self.ob_true_outlet_flux_for_guard[None]),
            "controller_target_outlet_flux": float(self.ob_target_outlet_flux[None]),
            "controller_measured_outlet_flux": float(self.ob_measured_outlet_flux[None]),
            "controller_raw_flux_error": float(self.ob_target_outlet_flux[None] - self.ob_measured_outlet_flux[None]),
            "controller_filtered_flux_error": float(self.ob_flux_error_filtered[None]),
            "controller_outlet_fluid_area": float(self.ob_outlet_fluid_area[None]),
            "controller_u_feedback": float(self.ob_flux_control_u_feedback[None]),
            "controller_u_feedback_abs": controller_feedback_abs,
            "controller_density_feedback": float(self.ob_flux_control_rho_feedback[None]),
            "controller_density_feedback_abs": controller_density_feedback_abs,
            "controller_delta_cap_u": float(self.open_boundary_flux_feedback_delta_cap_u),
            "controller_slew_alpha": float(self.open_boundary_flux_feedback_slew_alpha),
            "controller_authority_ratio": float(
                controller_feedback_abs / controller_cap_abs if controller_cap_abs else 0.0
            ),
            "controller_saturation_count_step": int(self.ob_flux_control_saturation_count_step[None]),
            "controller_saturation_count_run": controller_saturations,
            "controller_update_count_step": int(self.ob_flux_control_update_count_step[None]),
            "controller_update_count_run": controller_updates,
            "controller_saturation_fraction_run": float(
                controller_saturations / controller_updates if controller_updates else 0.0
            ),
            "controller_measure_plane_offset": int(self.open_boundary_flux_control_measure_plane_offset),
            "controller_target_scale": float(self.open_boundary_flux_control_target_scale),
            "controller_drop_guard_active_step": int(self.ob_drop_guard_active_step[None]),
            "controller_drop_guard_activation_count_run": int(self.ob_drop_guard_activation_count_run[None]),
            "controller_drop_guard_reference_flux": float(self.ob_drop_guard_reference_flux[None]),
            "controller_drop_guard_min_ratio": float(self.open_boundary_outlet_flux_drop_guard_min_ratio),
            "controller_drop_guard_activation_fraction_run": float(
                int(self.ob_drop_guard_activation_count_run[None]) / controller_updates if controller_updates else 0.0
            ),
        }

    @ti.kernel
    def Boundary_condition_legacy(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if (self.solid[0,j,k]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[1,j,k]>0):
                            self.F[0,j,k][s]=self.feq(s, self.rho_bcxl, self.v[1,j,k])
                        else:
                            self.F[0,j,k][s]=self.feq(s, self.rho_bcxl, self.v[0,j,k])

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if (self.solid[0,j,k]==0):
                    for s in ti.static(range(19)):
                        #F[0,j,k][s]=feq(LR[s], 1.0, bc_vel_x_left[None])-F[0,j,k,LR[s]]+feq(s,1.0,bc_vel_x_left[None])  #!!!!!!change velocity in feq into vector
                        self.F[0,j,k][s]=self.feq(s,1.0,self.bc_vel_x_left_dynamic[None])

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if (self.solid[self.nx-1,j,k]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[self.nx-2,j,k]>0):
                            self.F[self.nx-1,j,k][s]=self.feq(s, self.rho_bcxr, self.v[self.nx-2,j,k])
                        else:
                            self.F[self.nx-1,j,k][s]=self.feq(s, self.rho_bcxr, self.v[self.nx-2,j,k])

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if (self.solid[self.nx-1,j,k]==0):
                    for s in ti.static(range(19)):
                        #F[nx-1,j,k][s]=feq(LR[s], 1.0, bc_vel_x_right[None])-F[nx-1,j,k,LR[s]]+feq(s,1.0,bc_vel_x_right[None])  #!!!!!!change velocity in feq into vector
                        self.F[self.nx-1,j,k][s]=self.feq(s,1.0,ti.Vector(self.bc_vel_x_right))

         # Direction Y
        if ti.static(self.bc_y_left==1):
            for i,k in ti.ndrange((0,self.nx),(0,self.nz)):
                if (self.solid[i,0,k]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[i,1,k]>0):
                            self.F[i,0,k][s]=self.feq(s, self.rho_bcyl, self.v[i,1,k])
                        else:
                            self.F[i,0,k][s]=self.feq(s, self.rho_bcyl, self.v[i,0,k])

        if ti.static(self.bc_y_left==2):
            for i,k in ti.ndrange((0,self.nx),(0,self.nz)):
                if (self.solid[i,0,k]==0):
                    for s in ti.static(range(19)):
                        #self.F[i,0,k][s]=self.feq(self.LR[s], 1.0, self.bc_vel_y_left[None])-self.F[i,0,k][LR[s]]+self.feq(s,1.0,self.bc_vel_y_left[None])
                        self.F[i,0,k][s]=self.feq(s,1.0,ti.Vector(self.bc_vel_y_left))

        if ti.static(self.bc_y_right==1):
            for i,k in ti.ndrange((0,self.nx),(0,self.nz)):
                if (self.solid[i,self.ny-1,k]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[i,self.ny-2,k]>0):
                            self.F[i,self.ny-1,k][s]=self.feq(s, self.rho_bcyr, self.v[i,self.ny-2,k])
                        else:
                            self.F[i,self.ny-1,k][s]=self.feq(s, self.rho_bcyr, self.v[i,self.ny-1,k])

        if ti.static(self.bc_y_right==2):
            for i,k in ti.ndrange((0,self.nx),(0,self.nz)):
                if (self.solid[i,self.ny-1,k]==0):
                    for s in ti.static(range(19)):
                        #self.F[i,self.ny-1,k][s]=self.feq(self.LR[s], 1.0, self.bc_vel_y_right[None])-self.F[i,self.ny-1,k][self.LR[s]]+self.feq(s,1.0,self.bc_vel_y_right[None])
                        self.F[i,self.ny-1,k][s]=self.feq(s,1.0,ti.Vector(self.bc_vel_y_right))

        # Z direction
        if ti.static(self.bc_z_left==1):
            for i,j in ti.ndrange((0,self.nx),(0,self.ny)):
                if (self.solid[i,j,0]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[i,j,1]>0):
                            self.F[i,j,0][s]=self.feq(s, self.rho_bczl, self.v[i,j,1])
                        else:
                            self.F[i,j,0][s]=self.feq(s, self.rho_bczl, self.v[i,j,0])

        if ti.static(self.bc_z_left==2):
            for i,j in ti.ndrange((0,self.nx),(0,self.ny)):
                if (self.solid[i,j,0]==0):
                    for s in ti.static(range(19)):
                        #self.F[i,j,0][s]=self.feq(self.LR[s], 1.0, self.bc_vel_z_left[None])-self.F[i,j,0][self.LR[s]]+self.feq(s,1.0,self.bc_vel_z_left[None])
                        self.F[i,j,0][s]=self.feq(s,1.0,ti.Vector(self.bc_vel_z_left))

        if ti.static(self.bc_z_right==1):
            for i,j in ti.ndrange((0,self.nx),(0,self.ny)):
                if (self.solid[i,j,self.nz-1]==0):
                    for s in ti.static(range(19)):
                        if (self.solid[i,j,self.nz-2]>0):
                            self.F[i,j,self.nz-1][s]=self.feq(s, self.rho_bczr, self.v[i,j,self.nz-2])
                        else:
                            self.F[i,j,self.nz-1][s]=self.feq(s, self.rho_bczr, self.v[i,j,self.nz-1])

        if ti.static(self.bc_z_right==2):
            for i,j in ti.ndrange((0,self.nx),(0,self.ny)):
                if (self.solid[i,j,self.nz-1]==0):
                    for s in ti.static(range(19)):
                        #self.F[i,j,self.nz-1][s]=self.feq(self.LR[s], 1.0, self.bc_vel_z_right[None])-self.F[i,j,self.nz-1][self.LR[s]]+self.feq(s,1.0,self.bc_vel_z_right[None])
                        self.F[i,j,self.nz-1][s]=self.feq(s,1.0,ti.Vector(self.bc_vel_z_right))

    @ti.func
    def _regularized_population(self, s, target_rho, target_u, ni, nj, nk):
        neighbor_noneq = self.F[ni, nj, nk][s] - self.feq(s, self.rho[ni, nj, nk], self.v[ni, nj, nk])
        return self.feq(s, target_rho, target_u) + neighbor_noneq

    @ti.func
    def _limit_open_boundary_rho(self, target_rho):
        out = target_rho
        if ti.static(self.open_boundary_limiter_enabled):
            if out < self.open_boundary_rho_min:
                out = self.open_boundary_rho_min
            if out > self.open_boundary_rho_max:
                out = self.open_boundary_rho_max
        return out

    @ti.func
    def _limit_open_boundary_velocity(self, target_u):
        out = target_u
        if ti.static(self.open_boundary_limiter_enabled):
            norm = out.norm()
            if norm > self.open_boundary_u_max:
                out = out * (self.open_boundary_u_max / norm)
        return out

    @ti.func
    def _limit_open_boundary_population(self, value):
        out = value
        if ti.static(self.open_boundary_limiter_enabled):
            if ti.static(self.open_boundary_population_floor_enabled):
                if out < self.open_boundary_population_floor:
                    out = self.open_boundary_population_floor
        return out

    @ti.func
    def _limited_regularized_population(self, s, target_rho, target_u, ni, nj, nk):
        rho_limited = target_rho
        u_limited = target_u
        if ti.static(self.open_boundary_limiter_enabled):
            ti.atomic_add(self.ob_reconstructed_population_count_step[None], 1)
            ti.atomic_add(self.ob_reconstructed_population_count_run[None], 1)
            if rho_limited < self.open_boundary_rho_min:
                rho_limited = self.open_boundary_rho_min
                ti.atomic_add(self.ob_rho_clip_count_step[None], 1)
                ti.atomic_add(self.ob_rho_clip_count_run[None], 1)
            if rho_limited > self.open_boundary_rho_max:
                rho_limited = self.open_boundary_rho_max
                ti.atomic_add(self.ob_rho_clip_count_step[None], 1)
                ti.atomic_add(self.ob_rho_clip_count_run[None], 1)
            norm = u_limited.norm()
            if norm > self.open_boundary_u_max:
                u_limited = u_limited * (self.open_boundary_u_max / norm)
                ti.atomic_add(self.ob_velocity_clip_count_step[None], 1)
                ti.atomic_add(self.ob_velocity_clip_count_run[None], 1)
        neighbor_noneq = self.F[ni, nj, nk][s] - self.feq(s, self.rho[ni, nj, nk], self.v[ni, nj, nk])
        if ti.static(self.open_boundary_limiter_enabled):
            if neighbor_noneq > self.open_boundary_noneq_cap:
                neighbor_noneq = self.open_boundary_noneq_cap
                ti.atomic_add(self.ob_noneq_clip_count_step[None], 1)
                ti.atomic_add(self.ob_noneq_clip_count_run[None], 1)
            if neighbor_noneq < -self.open_boundary_noneq_cap:
                neighbor_noneq = -self.open_boundary_noneq_cap
                ti.atomic_add(self.ob_noneq_clip_count_step[None], 1)
                ti.atomic_add(self.ob_noneq_clip_count_run[None], 1)
        out = self.feq(s, rho_limited, u_limited) + neighbor_noneq
        if ti.static(self.open_boundary_limiter_enabled):
            if ti.static(self.open_boundary_population_floor_enabled):
                if out < self.open_boundary_population_floor:
                    out = self.open_boundary_population_floor
                    ti.atomic_add(self.ob_population_floor_count_step[None], 1)
                    ti.atomic_add(self.ob_population_floor_count_run[None], 1)
        return out

    @ti.func
    def _convective_outlet_population(self, s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k):
        extrapolated = self.F[ni, nj, nk][s]
        if self.solid[n2i, n2j, n2k] == 0:
            extrapolated = 2.0 * self.F[ni, nj, nk][s] - self.F[n2i, n2j, n2k][s]
        return self._limit_open_boundary_population(extrapolated)

    @ti.func
    def _bounded_scalar(self, value, limit):
        out = value
        if out > limit:
            out = limit
        if out < -limit:
            out = -limit
        return out

    @ti.func
    def _record_open_boundary_repair_correction(self, correction_abs, population_delta_abs):
        ti.atomic_add(self.ob_mass_balance_correction_count_step[None], 1)
        ti.atomic_add(self.ob_mass_balance_correction_count_run[None], 1)
        ti.atomic_add(self.ob_mass_balance_correction_abs_sum_step[None], correction_abs)
        ti.atomic_add(self.ob_mass_balance_correction_abs_sum_run[None], correction_abs)
        ti.atomic_add(self.ob_unknown_population_delta_abs_sum_step[None], population_delta_abs)
        ti.atomic_add(self.ob_unknown_population_delta_abs_sum_run[None], population_delta_abs)

    @ti.func
    def _record_open_boundary_flow_correction(self, correction_abs, outlet_flux_error):
        ti.atomic_add(self.ob_flow_correction_delta_abs_sum_step[None], correction_abs)
        ti.atomic_add(self.ob_flow_correction_delta_abs_sum_run[None], correction_abs)
        filtered = (
            (1.0 - self.open_boundary_flux_filter_alpha) * self.ob_flow_outlet_flux_error_filtered_run[None]
            + self.open_boundary_flux_filter_alpha * outlet_flux_error
        )
        self.ob_flow_outlet_flux_error_filtered_run[None] = filtered
        self.ob_flow_correction_gain_effective_step[None] = self.open_boundary_flux_feedback_gain_u

    @ti.func
    def _record_open_boundary_plane_flux_correction(self, correction_abs, population_delta_abs):
        self._record_open_boundary_repair_correction(correction_abs, population_delta_abs)
        ti.atomic_add(self.ob_flow_correction_delta_abs_sum_step[None], correction_abs)
        ti.atomic_add(self.ob_flow_correction_delta_abs_sum_run[None], correction_abs)
        self.ob_flow_correction_gain_effective_step[None] = self.open_boundary_flux_feedback_gain_u

    @ti.kernel
    def update_open_boundary_plane_flux_controller(self):
        self.ob_target_outlet_flux[None] = 0.0
        self.ob_measured_outlet_flux[None] = 0.0
        self.ob_outlet_fluid_area[None] = 0.0
        self.ob_near_outlet_flux_xminus1[None] = 0.0
        self.ob_near_outlet_flux_xminus2[None] = 0.0
        self.ob_near_outlet_flux_xminus3[None] = 0.0
        self.ob_true_outlet_flux_for_guard[None] = 0.0
        self.ob_drop_guard_active_step[None] = 0
        self.ob_drop_guard_reference_flux[None] = 0.0
        measure_i = ti.static(max(0, self.nx - 1 - self.open_boundary_flux_control_measure_plane_offset))
        near1_i = ti.static(max(0, self.nx - 2))
        near2_i = ti.static(max(0, self.nx - 3))
        near3_i = ti.static(max(0, self.nx - 4))
        for j, k in ti.ndrange((0, self.ny), (0, self.nz)):
            if self.solid[0, j, k] == 0:
                ti.atomic_add(self.ob_target_outlet_flux[None], self.rho[0, j, k] * self.v[0, j, k][0])
            if self.solid[measure_i, j, k] == 0:
                ti.atomic_add(
                    self.ob_measured_outlet_flux[None],
                    self.rho[measure_i, j, k] * self.v[measure_i, j, k][0],
                )
                ti.atomic_add(self.ob_outlet_fluid_area[None], 1.0)
            if self.solid[self.nx - 1, j, k] == 0:
                ti.atomic_add(
                    self.ob_true_outlet_flux_for_guard[None],
                    self.rho[self.nx - 1, j, k] * self.v[self.nx - 1, j, k][0],
                )
            if self.solid[near1_i, j, k] == 0:
                ti.atomic_add(
                    self.ob_near_outlet_flux_xminus1[None],
                    self.rho[near1_i, j, k] * self.v[near1_i, j, k][0],
                )
            if self.solid[near2_i, j, k] == 0:
                ti.atomic_add(
                    self.ob_near_outlet_flux_xminus2[None],
                    self.rho[near2_i, j, k] * self.v[near2_i, j, k][0],
                )
            if self.solid[near3_i, j, k] == 0:
                ti.atomic_add(
                    self.ob_near_outlet_flux_xminus3[None],
                    self.rho[near3_i, j, k] * self.v[near3_i, j, k][0],
                )
        self.ob_target_outlet_flux[None] = (
            self.open_boundary_flux_control_target_scale * self.ob_target_outlet_flux[None]
        )
        area = self.ob_outlet_fluid_area[None]
        if area <= 0.0:
            area = 1.0
            self.ob_outlet_fluid_area[None] = area
        raw_error = self.ob_target_outlet_flux[None] - self.ob_measured_outlet_flux[None]
        filtered = (
            (1.0 - self.open_boundary_flux_filter_alpha) * self.ob_flux_error_filtered[None]
            + self.open_boundary_flux_filter_alpha * raw_error
        )
        self.ob_flux_error_filtered[None] = filtered
        self.ob_flow_outlet_flux_error_filtered_run[None] = filtered
        requested_feedback = self.open_boundary_flux_feedback_gain_u * filtered / area
        bounded_feedback = self._bounded_scalar(requested_feedback, self.open_boundary_flux_correction_cap_u)
        previous_feedback = self.ob_flux_control_u_feedback[None]
        delta_limited_feedback = bounded_feedback
        if self.open_boundary_flux_feedback_delta_cap_u > 0.0:
            feedback_delta = self._bounded_scalar(
                bounded_feedback - previous_feedback,
                self.open_boundary_flux_feedback_delta_cap_u,
            )
            delta_limited_feedback = previous_feedback + feedback_delta
        next_feedback = previous_feedback + self.open_boundary_flux_feedback_slew_alpha * (
            delta_limited_feedback - previous_feedback
        )
        if ti.static(self.open_boundary_outlet_flux_drop_guard_enabled):
            reference_flux = ti.max(ti.abs(self.ob_target_outlet_flux[None]), ti.abs(self.ob_measured_outlet_flux[None]))
            self.ob_drop_guard_reference_flux[None] = reference_flux
            outlet_flux = ti.abs(self.ob_true_outlet_flux_for_guard[None])
            if reference_flux > 1.0e-12:
                if outlet_flux < self.open_boundary_outlet_flux_drop_guard_min_ratio * reference_flux:
                    if next_feedback < previous_feedback:
                        next_feedback = previous_feedback
                        self.ob_drop_guard_active_step[None] = 1
                        ti.atomic_add(self.ob_drop_guard_activation_count_run[None], 1)
        self.ob_flux_control_u_feedback[None] = next_feedback
        requested_rho_feedback = self.open_boundary_flux_feedback_gain_rho * filtered / area
        self.ob_flux_control_rho_feedback[None] = self._bounded_scalar(requested_rho_feedback, 0.01)
        self.ob_flow_correction_gain_effective_step[None] = self.open_boundary_flux_feedback_gain_u
        self.ob_flux_control_update_count_step[None] = 1
        ti.atomic_add(self.ob_flux_control_update_count_run[None], 1)
        if ti.abs(requested_feedback - bounded_feedback) > 1.0e-12:
            self.ob_flux_control_saturation_count_step[None] = 1
            ti.atomic_add(self.ob_flux_control_saturation_count_run[None], 1)

    @ti.func
    def _regularized_mass_balanced_population(self, s, target_rho, target_u, ni, nj, nk):
        rho_feedback = self._bounded_scalar(0.02 * (self.rho0 - self.rho[ni, nj, nk]), 0.01)
        velocity_feedback = self._bounded_scalar(0.05 * (self.vx_bcxl - target_u[0]), 0.02)
        repaired_u = target_u
        repaired_u[0] = target_u[0] + velocity_feedback
        repaired_rho = target_rho + rho_feedback
        before = self._regularized_population(s, target_rho, target_u, ni, nj, nk)
        after = self._regularized_population(s, repaired_rho, repaired_u, ni, nj, nk)
        self._record_open_boundary_repair_correction(ti.abs(rho_feedback) + ti.abs(velocity_feedback), ti.abs(after - before))
        return self._limit_open_boundary_population(after)

    @ti.func
    def _convective_mass_balanced_population(self, s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k):
        convective = self._convective_outlet_population(s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k)
        target_u = self.v[ni, nj, nk]
        regularized = self._regularized_mass_balanced_population(s, self.rho_bcxr, target_u, ni, nj, nk)
        repaired = convective + 0.15 * (regularized - convective)
        self._record_open_boundary_repair_correction(0.0, ti.abs(repaired - convective))
        return self._limit_open_boundary_population(repaired)

    @ti.func
    def _regularized_flux_matched_population(self, s, target_rho, target_u, ni, nj, nk):
        rho_feedback = self._bounded_scalar(
            self.open_boundary_flux_feedback_gain_rho * (self.rho0 - self.rho[ni, nj, nk]),
            0.01,
        )
        velocity_error = self.vx_bcxl - target_u[0]
        velocity_feedback = self._bounded_scalar(
            self.open_boundary_flux_feedback_gain_u * velocity_error,
            self.open_boundary_flux_correction_cap_u,
        )
        repaired_u = target_u
        repaired_u[0] = target_u[0] + velocity_feedback
        repaired_rho = target_rho + rho_feedback
        before = self._regularized_population(s, target_rho, target_u, ni, nj, nk)
        after = self._regularized_population(s, repaired_rho, repaired_u, ni, nj, nk)
        correction_abs = ti.abs(rho_feedback) + ti.abs(velocity_feedback)
        self._record_open_boundary_repair_correction(correction_abs, ti.abs(after - before))
        self._record_open_boundary_flow_correction(ti.abs(velocity_feedback), velocity_error)
        return self._limit_open_boundary_population(after)

    @ti.func
    def _convective_flux_matched_damped_population(self, s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k):
        convective = self._convective_outlet_population(s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k)
        target_u = self.v[ni, nj, nk]
        regularized = self._regularized_flux_matched_population(s, self.rho_bcxr, target_u, ni, nj, nk)
        blend = self.open_boundary_convective_blend_weight
        repaired = convective + blend * (regularized - convective)
        self._record_open_boundary_repair_correction(0.0, ti.abs(repaired - convective))
        self._record_open_boundary_flow_correction(ti.abs(repaired - convective), self.vx_bcxl - target_u[0])
        return self._limit_open_boundary_population(repaired)

    @ti.func
    def _regularized_plane_flux_controlled_population(self, s, target_rho, target_u, ni, nj, nk):
        rho_feedback = self.ob_flux_control_rho_feedback[None]
        velocity_feedback = self.ob_flux_control_u_feedback[None]
        repaired_u = target_u
        repaired_u[0] = target_u[0] + velocity_feedback
        repaired_rho = target_rho + rho_feedback
        before = self._regularized_population(s, target_rho, target_u, ni, nj, nk)
        after = self._regularized_population(s, repaired_rho, repaired_u, ni, nj, nk)
        correction_abs = ti.abs(rho_feedback) + ti.abs(velocity_feedback)
        self._record_open_boundary_plane_flux_correction(correction_abs, ti.abs(after - before))
        return self._limit_open_boundary_population(after)

    @ti.func
    def _convective_plane_flux_controlled_damped_population(self, s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k):
        convective = self._convective_outlet_population(s, bi, bj, bk, ni, nj, nk, n2i, n2j, n2k)
        target_u = self.v[ni, nj, nk]
        regularized = self._regularized_plane_flux_controlled_population(s, self.rho_bcxr, target_u, ni, nj, nk)
        blend = self.open_boundary_convective_blend_weight
        repaired = convective + blend * (regularized - convective)
        self._record_open_boundary_plane_flux_correction(ti.abs(repaired - convective), ti.abs(repaired - convective))
        return self._limit_open_boundary_population(repaired)

    @ti.kernel
    def apply_regularized_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, self.rho_bcxr, target_u, ni, j, k)

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_regularized_limited_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._limited_regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._limited_regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._limited_regularized_population(s, self.rho_bcxr, target_u, ni, j, k)

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._limited_regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_convective_pressure_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    n2i = self.nx - 3
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                        n2i = self.nx - 1
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._convective_outlet_population(
                            s, self.nx - 1, j, k, ni, j, k, n2i, j, k
                        )

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_regularized_mass_balanced_pressure_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_mass_balanced_population(s, self.rho_bcxr, target_u, ni, j, k)

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_convective_mass_balanced_pressure_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    n2i = self.nx - 3
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                        n2i = self.nx - 1
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._convective_mass_balanced_population(
                            s, self.nx - 1, j, k, ni, j, k, n2i, j, k
                        )

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_regularized_flux_matched_pressure_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_flux_matched_population(s, self.rho_bcxr, target_u, ni, j, k)

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_convective_flux_matched_damped_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    n2i = self.nx - 3
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                        n2i = self.nx - 1
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._convective_flux_matched_damped_population(
                            s, self.nx - 1, j, k, ni, j, k, n2i, j, k
                        )

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_regularized_plane_flux_controlled_pressure_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_plane_flux_controlled_population(
                            s, self.rho_bcxr, target_u, ni, j, k
                        )

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def apply_convective_plane_flux_controlled_damped_outlet_x_open_boundaries(self):
        if ti.static(self.bc_x_left==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_u = self.v[ni,j,k]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, self.rho_bcxl, target_u, ni, j, k)

        if ti.static(self.bc_x_left==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[0,j,k] == 0:
                    ni = 1
                    if self.solid[1,j,k] > 0:
                        ni = 0
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = self.bc_vel_x_left_dynamic[None]
                    for s in ti.static(UNKNOWN_X_MIN_POPULATIONS):
                        self.F[0,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

        if ti.static(self.bc_x_right==1):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    n2i = self.nx - 3
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                        n2i = self.nx - 1
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._convective_plane_flux_controlled_damped_population(
                            s, self.nx - 1, j, k, ni, j, k, n2i, j, k
                        )

        if ti.static(self.bc_x_right==2):
            for j,k in ti.ndrange((0,self.ny),(0,self.nz)):
                if self.solid[self.nx-1,j,k] == 0:
                    ni = self.nx - 2
                    if self.solid[self.nx-2,j,k] > 0:
                        ni = self.nx - 1
                    target_rho = self.rho[ni,j,k]
                    if target_rho <= 1.0e-6:
                        target_rho = self.rho0
                    target_u = ti.Vector(self.bc_vel_x_right)
                    for s in ti.static(UNKNOWN_X_MAX_POPULATIONS):
                        self.F[self.nx-1,j,k][s] = self._regularized_population(s, target_rho, target_u, ni, j, k)

    @ti.kernel
    def streaming3(self):
        for i in ti.grouped(self.rho):
            #print(i.x, i.y, i.z)
            if (self.solid[i]==0 and i.x<self.nx and i.y<self.ny and i.z<self.nz):
                self.rho[i] = 0
                self.v[i] = ti.Vector([0,0,0])
                self.f[i] = self.F[i]
                self.rho[i] += self.f[i].sum()

                for s in ti.static(range(19)):
                    self.v[i] += self.e_f[s]*self.f[i][s]

                f = self.cal_local_force(i.x, i.y, i.z)

                self.v[i] /= self.rho[i]
                self.v[i] += (f/2)/self.rho[i]

            else:
                self.rho[i] = self.rho0
                self.v[i] = ti.Vector([0,0,0])

    def get_max_v(self):
        self.max_v[None] = -1e10
        self.cal_max_v()
        return self.max_v[None]

    @ti.kernel
    def cal_max_v(self):
        for I in ti.grouped(self.rho):
            if self.solid[I] == 0:
                ti.atomic_max(self.max_v[None], self.v[I].norm())

    @ti.kernel
    def clear_coupling_fields(self):
        for I in ti.grouped(self.rho):
            self.solid_phi[I] = 0.0
            self.solid_mass[I] = 0.0
            self.solid_vel[I] = ti.Vector([0.0, 0.0, 0.0])
            self.cell_force[I] = ti.Vector([0.0, 0.0, 0.0])
            self.hydro_force[I] = ti.Vector([0.0, 0.0, 0.0])
            self.hydro_force_accum[I] = ti.Vector([0.0, 0.0, 0.0])
            self.reinit_flag[I] = ti.cast(0, ti.i8)
        self.mb_subcycle_force_sample_count[None] = 0
        self.mb_subcycle_force_accum_norm_max[None] = 0.0
        self.mb_subcycle_force_mean_norm_max[None] = 0.0

    @ti.kernel
    def copy_solid_to_static(self):
        for I in ti.grouped(self.rho):
            self.static_solid[I] = self.solid[I]
            self.old_solid[I] = self.solid[I]

    @ti.kernel
    def update_dynamic_solid(self, threshold: ti.f32):
        for I in ti.grouped(self.rho):
            prev_solid = self.solid[I]
            self.old_solid[I] = prev_solid

            dynamic_solid = self.solid_phi[I] >= threshold
            new_solid = 0
            if self.static_solid[I] != 0 or dynamic_solid:
                new_solid = 1

            self.solid[I] = ti.cast(new_solid, ti.i8)
            self.reinit_flag[I] = ti.cast(0, ti.i8)
            if prev_solid != 0 and new_solid == 0:
                self.reinit_flag[I] = ti.cast(1, ti.i8)

    @ti.kernel
    def reinitialize_new_fluid_cells(self):
        for I in ti.grouped(self.rho):
            if self.reinit_flag[I] == 1:
                reset_v = ti.Vector([0.0, 0.0, 0.0])
                if self.solid_vel[I].norm() > 0.0:
                    reset_v = self.solid_vel[I]

                self.rho[I] = self.rho0
                self.v[I] = reset_v
                for s in ti.static(range(19)):
                    feq_value = self.feq(s, self.rho0, reset_v)
                    self.f[I][s] = feq_value
                    self.F[I][s] = feq_value
                self.reinit_flag[I] = ti.cast(0, ti.i8)

    @ti.kernel
    def set_uniform_cell_force(self, fx: ti.f32, fy: ti.f32, fz: ti.f32):
        for I in ti.grouped(self.rho):
            if self.solid[I] == 0:
                self.cell_force[I] = ti.Vector([fx, fy, fz])
            else:
                self.cell_force[I] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def set_spherical_cell_force(
        self,
        cx: ti.f32,
        cy: ti.f32,
        cz: ti.f32,
        radius: ti.f32,
        fx: ti.f32,
        fy: ti.f32,
        fz: ti.f32,
    ):
        radius2 = radius * radius
        for I in ti.grouped(self.rho):
            dx = ti.cast(I.x, ti.f32) - cx
            dy = ti.cast(I.y, ti.f32) - cy
            dz = ti.cast(I.z, ti.f32) - cz
            inside = dx * dx + dy * dy + dz * dz <= radius2
            if self.solid[I] == 0 and inside:
                self.cell_force[I] = ti.Vector([fx, fy, fz])
            else:
                self.cell_force[I] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def set_dummy_solid_phi_block(
        self,
        x0: ti.i32,
        x1: ti.i32,
        y0: ti.i32,
        y1: ti.i32,
        z0: ti.i32,
        z1: ti.i32,
    ):
        for I in ti.grouped(self.rho):
            if x0 <= I.x and I.x < x1 and y0 <= I.y and I.y < y1 and z0 <= I.z and I.z < z1:
                self.solid_phi[I] = 1.0
                self.solid_mass[I] = 1.0
                self.solid_vel[I] = ti.Vector([0.01, 0.0, 0.0])

    @ti.kernel
    def build_dummy_hydro_force(self):
        for I in ti.grouped(self.rho):
            # Step 2 exports only a placeholder reaction. Real hydro force is deferred.
            self.hydro_force[I] = -self.cell_force[I]

    def get_stats(self):
        """
        Diagnostic-only. Do not call every production step because this copies Taichi fields to NumPy.
        """
        rho_np = self.rho.to_numpy()
        vel_np = self.v.to_numpy()
        solid_np = self.solid.to_numpy()
        force_np = self.cell_force.to_numpy()

        fluid = solid_np == 0
        if not np.any(fluid):
            stats = {
                "max_v": 0.0,
                "rho_min": float("nan"),
                "rho_max": float("nan"),
                "mass_total": 0.0,
                "force_norm_max": 0.0,
            }
        else:
            vel_norm = np.linalg.norm(vel_np[fluid], axis=1)
            force_norm = np.linalg.norm(force_np[fluid], axis=1)
            rho_fluid = rho_np[fluid]
            stats = {
                "max_v": float(np.max(vel_norm)),
                "rho_min": float(np.min(rho_fluid)),
                "rho_max": float(np.max(rho_fluid)),
                "mass_total": float(np.sum(rho_fluid)),
                "force_norm_max": float(np.max(force_norm)),
            }

        self.max_v[None] = stats["max_v"]
        if np.isfinite(stats["rho_min"]):
            self.rho_min[None] = stats["rho_min"]
        if np.isfinite(stats["rho_max"]):
            self.rho_max[None] = stats["rho_max"]
        self.mass_total[None] = stats["mass_total"]
        self.force_norm_max[None] = stats["force_norm_max"]
        return stats


    def set_bc_vel_x1(self, vel):
        self.bc_x_right = 2
        self.vx_bcxr = vel[0]; self.vy_bcxr = vel[1]; self.vz_bcxr = vel[2];

    def set_bc_vel_x0(self, vel):
        self.bc_x_left = 2
        self.vx_bcxl = vel[0]; self.vy_bcxl = vel[1]; self.vz_bcxl = vel[2];
        self.bc_vel_x_left = [self.vx_bcxl, self.vy_bcxl, self.vz_bcxl]
        self.bc_vel_x_left_dynamic[None] = self.bc_vel_x_left

    def set_bc_vel_y1(self, vel):
        self.bc_y_right = 2
        self.vx_bcyr = vel[0]; self.vy_bcyr = vel[1]; self.vz_bcyr = vel[2];

    def set_bc_vel_y0(self, vel):
        self.bc_y_left = 2
        self.vx_bcyl = vel[0]; self.vy_bcyl = vel[1]; self.vz_bcyl = vel[2];

    def set_bc_vel_z1(self, vel):
        self.bc_z_right = 2
        self.vx_bczr = vel[0]; self.vy_bczr = vel[1]; self.vz_bczr = vel[2];

    def set_bc_vel_z0(self, vel):
        self.bc_z_left = 2
        self.vx_bczl = vel[0]; self.vy_bczl = vel[1]; self.vz_bczl = vel[2];

    def set_bc_rho_x0(self, rho):
        self.bc_x_left = 1
        self.rho_bcxl = rho

    def set_bc_rho_x1(self, rho):
        self.bc_x_right = 1
        self.rho_bcxr = rho

    def set_bc_rho_y0(self, rho):
        self.bc_y_left = 1
        self.rho_bcyl = rho

    def set_bc_rho_y1(self, rho):
        self.bc_y_right = 1
        self.rho_bcyr = rho

    def set_bc_rho_z0(self, rho):
        self.bc_z_left = 1
        self.rho_bczl = rho

    def set_bc_rho_z1(self, rho):
        self.bc_z_right = 1
        self.rho_bczr = rho


    def set_viscosity(self,niu):
        self.niu = niu

    def set_force(self,force):
        self.fx = force[0]; self.fy = force[1]; self.fz = force[2];



    def export_VTK(self, n, out_prefix="./LBMFluid"):
        if gridToVTK is None:
            raise RuntimeError("pyevtk is required for LBMFluid3D.export_VTK()")

        velocity = self.v.to_numpy()
        solid_velocity = self.solid_vel.to_numpy()
        cell_force = self.cell_force.to_numpy()
        hydro_force = self.hydro_force.to_numpy()

        gridToVTK(
                out_prefix+"_"+str(n),
                self.x,
                self.y,
                self.z,
                #cellData={"pressure": pressure},
                pointData={ "Solid": np.ascontiguousarray(self.solid.to_numpy()),
                            "StaticSolid": np.ascontiguousarray(self.static_solid.to_numpy()),
                            "OldSolid": np.ascontiguousarray(self.old_solid.to_numpy()),
                            "ReinitFlag": np.ascontiguousarray(self.reinit_flag.to_numpy()),
                            "rho": np.ascontiguousarray(self.rho.to_numpy()),
                            "solid_phi": np.ascontiguousarray(self.solid_phi.to_numpy()),
                            "solid_mass": np.ascontiguousarray(self.solid_mass.to_numpy()),
                            "velocity": (   np.ascontiguousarray(velocity[0:self.nx,0:self.ny,0:self.nz,0]),
                                            np.ascontiguousarray(velocity[0:self.nx,0:self.ny,0:self.nz,1]),
                                            np.ascontiguousarray(velocity[0:self.nx,0:self.ny,0:self.nz,2])),
                            "solid_vel": (  np.ascontiguousarray(solid_velocity[0:self.nx,0:self.ny,0:self.nz,0]),
                                            np.ascontiguousarray(solid_velocity[0:self.nx,0:self.ny,0:self.nz,1]),
                                            np.ascontiguousarray(solid_velocity[0:self.nx,0:self.ny,0:self.nz,2])),
                            "cell_force": ( np.ascontiguousarray(cell_force[0:self.nx,0:self.ny,0:self.nz,0]),
                                            np.ascontiguousarray(cell_force[0:self.nx,0:self.ny,0:self.nz,1]),
                                            np.ascontiguousarray(cell_force[0:self.nx,0:self.ny,0:self.nz,2])),
                            "hydro_force": (np.ascontiguousarray(hydro_force[0:self.nx,0:self.ny,0:self.nz,0]),
                                            np.ascontiguousarray(hydro_force[0:self.nx,0:self.ny,0:self.nz,1]),
                                            np.ascontiguousarray(hydro_force[0:self.nx,0:self.ny,0:self.nz,2]))
                            }
            )

    def get_moving_boundary_stats(self):
        """
        Diagnostic-only. Reads the last moving-bounceback streaming reductions to Python.
        """
        fluid_impulse = self.bb_net_fluid_impulse[None].to_numpy()
        solid_force = self.bb_net_solid_force[None].to_numpy()
        return {
            "bb_link_count": int(self.bb_link_count[None]),
            "bb_max_correction": float(self.bb_max_correction[None]),
            "bb_net_fluid_impulse": tuple(float(v) for v in fluid_impulse),
            "bb_net_solid_force": tuple(float(v) for v in solid_force),
        }

    def get_moving_boundary_directional_stats(self):
        """
        Diagnostic-only. Returns per-D3Q19-direction moving-boundary bounce-back reductions.
        """
        return {
            "link_count_by_dir": self.bb_link_count_by_dir.to_numpy(),
            "fluid_impulse_by_dir": self.bb_fluid_impulse_by_dir.to_numpy(),
            "solid_force_by_dir": self.bb_solid_force_by_dir.to_numpy(),
            "correction_abs_sum_by_dir": self.bb_correction_abs_sum_by_dir.to_numpy(),
            "correction_abs_max_by_dir": self.bb_correction_abs_max_by_dir.to_numpy(),
        }

    def get_moving_boundary_accumulation_stats(self):
        return {
            "mb_subcycle_force_sample_count": int(self.mb_subcycle_force_sample_count[None]),
            "mb_subcycle_force_accum_norm_max": float(self.mb_subcycle_force_accum_norm_max[None]),
            "mb_subcycle_force_mean_norm_max": float(self.mb_subcycle_force_mean_norm_max[None]),
        }

    def step(self):
        self.colission()
        self.streaming1()
        self.Boundary_condition()
        self.streaming3()

    def step_moving_bounceback(self):
        self.clear_moving_boundary_diagnostics()
        self.colission()
        self.streaming_moving_bounceback()
        self.finalize_moving_boundary_diagnostics()
        self.Boundary_condition()
        self.streaming3()





'''
time_init = time.time()
time_now = time.time()
time_pre = time.time()
dt_count = 0


lb3d = LB3D_Solver_Single_Phase(50,50,50)

lb3d.init_geo('./geo_cavity.dat')
lb3d.set_bc_vel_x1([0.0,0.0,0.1])
lb3d.init_simulation()


for iter in range(50000+1):
    lb3d.step()

    if (iter%1000==0):

        time_pre = time_now
        time_now = time.time()
        diff_time = int(time_now-time_pre)
        elap_time = int(time_now-time_init)
        m_diff, s_diff = divmod(diff_time, 60)
        h_diff, m_diff = divmod(m_diff, 60)
        m_elap, s_elap = divmod(elap_time, 60)
        h_elap, m_elap = divmod(m_elap, 60)

        print('----------Time between two outputs is %dh %dm %ds; elapsed time is %dh %dm %ds----------------------' %(h_diff, m_diff, s_diff,h_elap,m_elap,s_elap))
        print('The %dth iteration, Max Force = %f,  force_scale = %f\n\n ' %(iter, 10.0,  10.0))

        if (iter%10000==0):
            lb3d.export_VTK(iter)



#ti.profiler.print_scoped_profiler_info()
#ti.print_profile_info()
#ti.profiler.print_kernel_profiler_info()  # default mode: 'count'

#ti.profiler.print_kernel_profiler_info('trace')
#ti.profiler.clear_kernel_profiler_info()  # clear all records

'''
