# Device Variants and Support Policy

All resources below are **planning envelopes**, not measured benchmarks or guarantees.

| Variant | CPU / example | Indicative RAM | OS strategy | AI mode |
|---|---|---:|---|---|
| Nano | tiny Cortex-M | 64–256 KiB | bare metal / minimal RTOS | fixed-point event classifier |
| Tiny | STM32-class Cortex-M | 256 KiB–2 MiB | Zephyr | TinyML on demand |
| Edge | Raspberry Pi 4B ARM64 | 512 MiB–4 GiB | Yocto Linux | local bounded inference |
| Industrial | industrial ARM gateway plus MCU | 1–8 GiB | Linux + RTOS boundary | predictive maintenance |
| Gateway | ARM64 / x86-64 | 4–16 GiB+ | Linux | optional multi-device inference |

## Support levels
**PLANNED:** design only. **EXPERIMENTAL:** image boots and tests reproducibly on specified hardware. **SUPPORTED:** update and recovery, security constraints, soak, regression and documentation are all accepted. **DEPRECATED:** migration and support deadline published.

Initial targets: Raspberry Pi 4B (Edge); an exact Cortex-M board and revision must be selected before Tiny acceptance. A target enters SUPPORTED only after recorded hardware proof.

## Non-negotiable differences
MMU, root of trust, A/B update, timing guarantees, NPU and persistent storage vary by board. Advertise absence as `UNSUPPORTED`; do not fabricate capability values.
