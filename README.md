# AION OS

**AI-native embedded operating-system platform** · **Status: pre-alpha / specification and policy-engine prototype** · **License: Apache-2.0**

AION OS is a family of embedded operating-system distributions for ARM-first IoT. It defines portable device capabilities, bounded AI execution, authorization, health telemetry and update semantics across different kernels. **It is not yet a bootable OS.** No hardware, timing, power, or security-certification claims have been validated.

> AI may advise the system. It must never be required for the system to boot, perform critical I/O, or enforce safety policy.

## Architecture

```text
  Device management / CLI / local applications (future)
  -----------------------------------------------------
  Versioned capability & health APIs | audit events
  -----------------------------------------------------
  AI event runtime | resource admission | policy gate
  -----------------------------------------------------
  OS services | identity | signed updates | telemetry
  -----------------------------------------------------
     Zephyr / Cortex-M        Embedded Linux / ARM64
```

The AI layer runs outside interrupt and hard-real-time control paths. Privileged actions require a typed, explicitly authorized policy decision. The core OS continues operating when inference is unavailable.

## Variants

| Edition | Target | Kernel strategy | Initial status |
|---|---|---|---|
| Nano | tightly constrained MCU | bare metal/RTOS | planned |
| Tiny | ARM Cortex-M | Zephyr | planned |
| Edge | Raspberry Pi 4B ARM64 | embedded Linux / Yocto | first planned hardware target |
| Industrial | industrial control gateway | Linux + dedicated real-time controller | planned |
| Gateway | ARM64 or x86-64 nodes | embedded Linux | planned |

**No platform is currently certified or supported.** Board-specific secure boot, cryptographic roots of trust, hardware acceleration and A/B update capability must be verified individually.

## Developer quickstart (policy library only)

Requires a locally installed stable Rust toolchain; no paid services are needed.

```sh
cargo test --workspace --all-targets
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
```

This validates the small host-side policy prototype, **not** kernel integration or actual device isolation.

## Project documents

- [Product vision](docs/PRODUCT_VISION.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Variant matrix](docs/VARIANTS.md)
- [Decision: AI outside kernel](docs/adr/0001-kernel-boundary.md)
- [Spec Kit constitution](.specify/memory/constitution.md)
- [Platform specification](specs/001-ai-native-platform/spec.md)
- [Engineering plan](specs/001-ai-native-platform/plan.md)
- [Task list](specs/001-ai-native-platform/tasks.md)
- [Acceptance evidence checklist](specs/001-ai-native-platform/checklists/acceptance.md)
- [Policy contract](specs/001-ai-native-platform/contracts/policy-v0.md)
- [Contribution guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Project status

The first deliverable is a documented foundation and a **pure, side-effect-free policy decision library**. There is no privileged executor, hardware integration, signed update mechanism, or boot image yet. Test results are meaningful only for what they actually exercise.

See the [Apache 2.0 license](LICENSE). Contributions are welcome via reviewed pull requests. Do not report vulnerabilities in public issues.
