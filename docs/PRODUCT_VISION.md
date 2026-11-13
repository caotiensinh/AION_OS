# Product Vision — AION OS

**Version:** 0.1 · **Date:** 2026-11-13 · **Phase:** exploratory specification

## Vision
Build an ARM-first family of embedded operating systems that treats AI as a supervised, resource-bounded system capability, rather than an application with uncontrolled privilege.

## Users
1. Embedded developers shipping low-power intelligent sensors and actuators.
2. Edge AI developers deploying cameras, microphones and on-premises inference.
3. Industrial platform teams managing heterogeneous gateways and field devices.
4. Fleet operators who need offline continuity, diagnosability and safe updates.

## Core promise
- **Operates without AI:** boot, telemetry, essential I/O and recovery are independent.
- **Bounded AI:** deadlines, queues and resource budgets protect critical tasks.
- **Controlled autonomy:** AI proposes actions; an independent, default-deny policy gate authorizes actions.
- **Portable contracts:** versioned capabilities and failure semantics across MCU and Linux targets.
- **Verifiable updates:** target-aware signing, compatibility checks, health checks and rollback, where supported.
- **Inspectable behavior:** audit trails, reproducible build inputs, test artifacts and explicit support levels.

## Product boundaries
Not in v0.1: a novel universal kernel; desktop/mobile UI; full autonomous system repair; industrial functional-safety certification; universal NPU/driver support; cloud-dependent control; claims of secure boot on every board.

## Product success gates
G0: repository governance, documented architecture and host policy-unit tests.
G1: pinned ARM64 image build, reproducible provenance and observable offline boot.
G2: Linux resource-budgeted AI agent and admission-control stress validation.
G3: Zephyr MCU prototype with common contract fixtures and bounded ISR behavior.
G4: signed update lifecycle, fault injection, hardware measurements and 72h soak.

A gate passes only when changes and test evidence are persisted at a specific commit. No product percentage can be inferred from documentation completion.
