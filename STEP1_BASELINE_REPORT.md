# Step 1 Baseline Report

## 1. Environment

- Date: 2026-06-18
- OS: Windows-10-10.0.26200-SP0
- Python: 3.10.18 at `D:\working\taichi\env\python.exe`
- Taichi: 1.7.4
- NumPy: 1.26.4
- pyevtk: 1.7.0
- sympy: 1.14.0
- pytest: 9.1.0
- GPU: NVIDIA GeForce GTX 1660
- NVIDIA driver: 591.86
- CUDA version reported by nvidia-smi: 13.1

Notes:

- The default `python` on PATH is not the Step 1 environment. Use `D:\working\taichi\env\python.exe`.
- `requirements.txt` was generated from the active environment with `pip freeze`.
- `environment.yml` records the intended reproducible Python 3.10 environment.

## 2. Repository

- taichi_LBM3D URL: https://github.com/yjhp1016/taichi_LBM3D
- local path: `external/taichi_LBM3D`
- commit hash: `fe49e3f609b2038cbf93c8bd453ffc5c2bf98e4c`
- scope used in Step 1: `Single_phase` only

## 3. Backend Test

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\check_taichi_backend.py
```

Result:

- CPU backend: OK, Taichi arch `x64`
- GPU backend: OK, Taichi arch `cuda`
- CPU max error: `0.000000e+00`
- GPU max error: `0.000000e+00`
- log: `logs/check_taichi_backend.log`

## 4. LBM Single Phase Baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_lbm_cavity_baseline.py
```

Result:

- solver: `external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py`
- backend: GPU, Taichi arch `cuda`
- grid: `32 x 32 x 32`
- geometry: generated all-fluid smoke geometry, `outputs/lbm_cavity/geo_cavity_32.dat`
- boundary condition: `set_bc_vel_x1([0.0, 0.0, 0.03])`
- viscosity input: `0.16667`
- finished steps: 500
- max_v range: `3.000000e-02` to `3.000000e-02`
- rho range: `1.000000e+00` to `1.000001e+00`
- rho issue: no NaN/Inf detected
- velocity issue: no NaN/Inf detected
- VTK output: yes, `outputs/lbm_cavity/LB_SingelPhase_500.vtr`
- log: `logs/lbm_cavity_baseline.log`

Notes:

- This is an independent Single_phase LBM smoke baseline only.
- The run emits Taichi warnings about 19x19 MRT matrices being unrolled and a geometry dtype precision warning. These are warnings from the upstream solver path, not runtime failures.
- No coupling, moving boundary, IBM, MPM feedback, or squid model was added.

## 5. MPM 3D Baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_mpm3d_baseline.py
```

Result:

- backend: GPU, Taichi arch `cuda`
- grid: `32 x 32 x 32`
- particles: 8192
- finished steps: 50
- final min_y: `0.347983`
- final max_y: `0.647911`
- final max_speed: `1.999203e-01`
- final min_J: `1.000000`
- particle position issue: no NaN/Inf detected
- J issue: `J > 0` for the smoke run
- npy output: yes, `outputs/mpm3d/mpm3d_positions.npy`
- log: `logs/mpm3d_baseline.log`

Notes:

- This is only a standalone 3D MPM smoke test.
- It is not the final solid model for FSI and does not implement fixed-corotated elasticity or LBM-MPM force exchange.

## 6. Output Files

Required artifacts produced:

- `requirements.txt`
- `environment.yml`
- `logs/check_taichi_backend.log`
- `logs/lbm_cavity_baseline.log`
- `logs/mpm3d_baseline.log`
- `outputs/lbm_cavity/geo_cavity_32.dat`
- `outputs/lbm_cavity/LB_SingelPhase_500.vtr`
- `outputs/mpm3d/mpm3d_positions.npy`

## 7. Acceptance Checklist

- [x] Python environment is documented and repeatable through `environment.yml`
- [x] `taichi import` succeeds
- [x] `numpy import` succeeds
- [x] `pyevtk import` succeeds
- [x] `sympy import` succeeds
- [x] Taichi CPU backend runs successfully
- [x] Taichi GPU backend runs successfully
- [x] LBM Single_phase case runs for at least 500 steps
- [x] LBM `max_v` is finite
- [x] LBM `rho` is finite
- [x] LBM writes VTK output
- [x] MPM 3D baseline runs for at least 50 steps
- [x] MPM particle positions are finite
- [x] MPM `J` remains positive
- [x] All run logs are saved under `logs/`
- [x] Baseline report is written

## 8. Decision

Can proceed to Step 2?

- [x] Yes
- [ ] No

Blocking issues:

- None for Step 1.

Carry-forward caution:

- Step 1 proves environment, standalone LBM, and standalone MPM baselines only.
- Step 2 must still design the coupling carefully. Do not treat this as evidence that LBM-MPM FSI is already stable.
