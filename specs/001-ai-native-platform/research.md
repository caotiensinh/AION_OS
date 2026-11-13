# Engineering research and open decisions

This file documents design assumptions, not benchmark results.

## Kernel/BSP choices
- **Edge:** Yocto for minimal, reproducible Linux images. Pin exact release, BSP layer revisions, source tarball digests and toolchain artifacts before first image build.
- **Tiny:** Zephyr for deterministic MCU scheduling, build tooling and well-defined devicetree/Kconfig support. Exact board and versions TBD.
- **Policy:** pure Rust host core with no external crates. This is not yet a validated C ABI or RTOS component.

## Risks to resolve by experiment
1. Pi 4B update/bootloader and power-loss recovery path; do not assume A/B rollback.
2. Real-time latency isolation under CPU/memory and inference saturation.
3. Platform-specific entropy, clocks, hardware identity and secret storage.
4. Model compatibility with memory size and inference accelerator availability.
5. Reproducible build across pinned host environments; document any nondeterminism.
6. Firmware license notices and security advisories for BSP/toolchain dependencies.

## Research outputs required
For each hardware target: board revision, kernel/bootloader versions, devicetree/BSP SHA, peripherals, memory map, observed power budget, update strategy and recovery evidence. All source claims must be dated and traceable before a release branch is cut.
