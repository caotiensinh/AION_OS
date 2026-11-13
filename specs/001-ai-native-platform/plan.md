# Implementation Plan

**Phase G0 — Repository foundation:** public-facing documentation, architecture decisions, security disclosure, contribution guidance, policy reference implementation and host tests. **Acceptance:** reviewed commit and passing local/CI checks.

**Phase G1 — ARM64 image:** pin Yocto release and BSP layers by commit; build/boot Raspberry Pi 4B image; watchdog, serial logging, offline networking, image provenance. **Acceptance:** AT-01..04, AT-25.

**Phase G2 — Resource and AI runtime:** bounded event intake, admission, model digest verification, non-root service and cgroup limits; benchmark under saturation. **Acceptance:** AT-05..13, AT-19.

**Phase G3 — MCU interoperability:** select exact Zephyr board, pin toolchain, implement event adapter and common fixtures; prove ISR nonblocking. **Acceptance:** AT-14, AT-21..24.

**Phase G4 — Secure update:** choose and validate boot chain per board; staged signed update, health confirmation and failure rollback. **Acceptance:** AT-15..20, AT-26.

**Phase G5 — Hardening and release:** fuzz parsers, execute 72h soak, inspect license/SBOM/security findings. **Acceptance:** AT-27..28 and all P0 gates.

## Dependency graph
G0 -> G1 / G2 / G3 (partially parallel after contract freeze) -> G4 -> G5.

## Risk register
Supply-chain/BSP drift: pin and hash dependencies. Unsupported silicon root-of-trust: disclose unsupported and restrict claims. RT scheduler starvation: explicit stress benchmarks and AI disable test. Physical power-loss proof: requires test fixture; mark pending, not PASS.

## Workflow
`SPECIFY -> PLAN -> TASKS -> IMPLEMENT -> TEST -> VERIFY -> PERSIST`. Do not mark a stage complete without recorded acceptance evidence.
