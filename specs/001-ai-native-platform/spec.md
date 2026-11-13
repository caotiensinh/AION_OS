# Specification: AI-Native Embedded Platform

**Feature:** 001-ai-native-platform · **Status:** baseline draft · **Date:** 2026-11-13

## P0 user stories
- **US-01 Offline boot:** On ARM64 hardware, disable network and AI; essential I/O, logs and watchdog continue (AT-01..04).
- **US-02 Safe proposals:** A rejected, expired, replayed or unknown proposed action triggers no privileged work (AT-05..09).
- **US-03 Bounded inference:** Under overload, memory, queue and deadline limits are respected; core I/O keeps its measured bounds (AT-10..14).
- **US-04 Recoverable updates:** Only authentic and board-compatible images are accepted; interrupted installation preserves bootability (AT-15..20).
## P1 user stories
- **US-05 Shared semantics:** Tiny and Edge expose versioned capability/health contracts with explicit unsupported fields (AT-21..24).
- **US-06 Evidence:** Build source pins, hashes, SBOM, reproducible test commands and operational logs are retained (AT-25..28).

## Functional requirements
FR-001 bootable ARM64 image and board manifest; FR-002 AI-off OS availability; FR-003 versioned capabilities; FR-004 offline health; FR-005 default-deny typed action policy; FR-006 digest-pinned model manifest; FR-007 bounded inference scheduler; FR-008 isolated Linux AI process; FR-009 statically budgeted MCU runtime; FR-010 target-appropriate secrets/signatures; FR-011 staged update and rollback; FR-012 structured audit events; FR-013 offline-first operation; FR-014 shared contract fixtures; FR-015 release SBOM/license/provenance; FR-016 structured operational CLI.

## Nonfunctional requirements
NFR-001 board-specific CPU/RAM budgets with measurements; NFR-002 no synchronous inference in IRQ or hard-real-time paths; NFR-003 power-failure-safe updates where bootloader permits; NFR-004 no secrets or unsolicited outbound traffic; NFR-005 dependency pinning; NFR-006 positive/negative/boundary, fault and soak testing; NFR-007 unknown actions rejected and major-version-compatible schemas.

## Hard limitations
No novel kernel, universal driver coverage, functional-safety certification or unverified autonomous repair. Raspberry Pi 4B ARM64 is the first proposed physical target; no physical test has yet passed.

## Definition of Done
P0 tests pass on specified hardware with reproducible evidence. Unit tests alone are insufficient for OS/firmware PASS.
