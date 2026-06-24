from step93_common import run_named_audit
from src.mpm_lbm.evidence.step93_taichi_ggui_visualization_enablement_guard import (
    build_step93_taichi_ggui_visualization_enablement_guard,
)


def main():
    run_named_audit(
        build_step93_taichi_ggui_visualization_enablement_guard,
        "outputs/step93_taichi_ggui_visualization_enablement_guard",
        "logs/step93_taichi_ggui_visualization_enablement_guard.log",
        "step93_taichi_ggui_visualization_enablement_guard_pass",
        "[OK] Step93 Taichi GGUI visualization enablement guard finished",
        "taichi_ggui_visualization_enablement_guard",
    )


if __name__ == "__main__":
    main()
