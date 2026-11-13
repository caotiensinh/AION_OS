# Architecture — Trust Boundaries and Data Flow

## System model
```text
sensor IRQ --> deterministic driver/control task --> bounded event queue
                                               |        |
                                               |        v
                                               |  AI runtime / inference
                                               |        |
                                               |  untrusted typed proposal
                                               |        v
                                               |  policy gate (default deny)
                                               |        |
                                               |  authorized executor (future)
                                               v
                                        core device I/O
```

The executor is **not** implemented in the current prototype. The Rust policy crate only returns a decision; it does not issue system calls or change device state.

## Layers
1. **BSP/kernel:** Zephyr on constrained MCUs; Linux via Yocto for ARM64. Never run inference synchronously in IRQ or hard-real-time paths.
2. **Core services:** networking, storage, clock, watchdog, telemetry, identity and update supervisor.
3. **Capability interface:** versioned descriptions of supported sensors, compute, security capabilities and unsupported features.
4. **Intelligence subsystem:** event admission, budgets, model manifest validation, inference adapters and error handling.
5. **Policy and audit:** independently configured allowlist, explicit principal/target/scope, expiry, replay protection at the transport/executor boundary, auditable outcomes.
6. **Operations:** local CLI and optional authenticated fleet management. No mandatory cloud dependency.

## Threat boundaries
- Model outputs, telemetry from remote devices and incoming commands are untrusted.
- AI is never root by default; executable privileges are separated from inference.
- Policy decisions must not grant authority by themselves: executor revalidates identity, capabilities, replay and state immediately before action.
- Secrets never enter ordinary diagnostic exports.
- Fail closed on parse failures, identity mismatch, expired intent and unknown action.
- Keep independent physical safety controls and hardware watchdogs for actuators.

## Reliability
- Queue overflow => reject admission and record a rate-limited diagnostic.
- Model unavailable => deterministic rule-based fallback.
- AI crash => core services continue.
- Bad firmware update => retain previous known-good image where supported.
- Network disconnected => local operation remains available.

## Design decisions
- Rust for portable host-side policy library; C/RTOS integration by an explicit future ABI.
- No blanket claim of a shared binary or common kernel across Cortex-M and Cortex-A.
- Time, device identity and replay prevention are security-sensitive external dependencies; the current prototype does not implement their verification.
