import sys

import numpy as np
import taichi as ti


N = 1024


def run_backend_test(arch, name):
    print(f"\n=== Testing backend: {name} ===")

    try:
        ti.reset()
        ti.init(arch=arch, default_fp=ti.f32, kernel_profiler=False)

        x = ti.field(dtype=ti.f32, shape=N)
        y = ti.field(dtype=ti.f32, shape=N)

        @ti.kernel
        def fill():
            for i in range(N):
                x[i] = i * 0.5
                y[i] = x[i] * 2.0 + 1.0

        fill()

        y_np = y.to_numpy()
        expected = np.arange(N, dtype=np.float32) + 1.0
        err = float(np.max(np.abs(y_np - expected)))

        print(f"max error = {err:.6e}")
        assert err < 1e-5

        print(f"[OK] {name} backend works.")
        return True

    except Exception as exc:
        print(f"[FAILED] {name} backend failed:")
        print(exc)
        return False


if __name__ == "__main__":
    print("Python:", sys.version)
    print("Taichi:", ti.__version__)

    cpu_ok = run_backend_test(ti.cpu, "CPU")
    gpu_ok = run_backend_test(ti.gpu, "GPU")

    print("\n=== Summary ===")
    print("CPU:", "OK" if cpu_ok else "FAILED")
    print("GPU:", "OK" if gpu_ok else "FAILED")

    if not cpu_ok:
        raise RuntimeError("CPU backend must work before continuing.")
    if not gpu_ok:
        raise RuntimeError("GPU backend is required for this Step 1 baseline.")
