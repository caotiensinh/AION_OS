# AION Capability / Health Wire Protocol v1

**Status:** Experimental — serialization contract; not a remotely trusted command protocol.

## Motivation
Tiny (MCU) and Edge (Linux) share a compact, bounded way to report what a device supports and its local health without requiring heap allocation or JSON parsing on an MCU.

## Binary layout (exactly 32 bytes, little-endian)

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 4 | ASCII magic `AION` |
| 4 | 1 | protocol major version, exactly `1` |
| 5 | 1 | record kind: `1` capability, `2` health |
| 6 | 1 | status: capability `0 Unknown, 1 Unsupported, 2 Supported`; health `0 Invalid, 1 Valid` |
| 7 | 1 | reserved, MUST be zero |
| 8 | 2 | feature/metric identifier (u16) |
| 10 | 2 | source identifier (u16) |
| 12 | 4 | capability limit (u32); health value (i32) |
| 16 | 8 | monotonic milliseconds since device boot (u64) |
| 24 | 4 | reason code (u32) |
| 28 | 4 | reserved, MUST be zero |

Unknown/Unsupported capability MUST have zero limit, and Supported MUST have reason zero. Invalid health MUST have zero value, and Valid MUST have reason zero. All unknown status values, kinds, versions, reserved bits, short or long frames are rejected.

Identifiers, units, bounds and reason-code registries must be versioned and agreed by both ends; until then, every identifier's physical interpretation is application-specific. An unknown feature ID MUST NOT imply support.

## Golden fixture

A supported capability: feature 7, source 2, limit 2048, uptime 123456ms, reason 0:

```text
41 49 4f 4e 01 01 02 00 07 00 02 00 00 08 00 00
40 e2 01 00 00 00 00 00 00 00 00 00 00 00 00 00
```

## Trust and limitations
- **Not authenticated, encrypted, signed, freshness-checked or replay-resistant.**
- This frame is a telemetry data format, NOT an authorization token.
- Transport bounds, peer identity, anti-replay, integrity, audit and privileged action execution are separate mandatory components.
- Do not expose untrusted frames to safety-critical controls or infer secured hardware identities.
- The Rust `aion-contract` library uses `#![no_std]`, fixed-size frames and no heap; actual Cortex-M deployment remains untested.

## Compatibility rules
Major-version mismatch => reject. Unknown record type => reject. Producer must write reserved bytes as zero. Consumers reject noncanonical reserved data. Future extensions require explicit new major version, not reinterpretation of reserved bytes.

## Acceptance mapping
T009: wire layout and codec fixtures implemented. AT-21/22: still TODO until two physical targets exchange and correctly interpret data. AT-23/24: remain MCU hardware tests.
