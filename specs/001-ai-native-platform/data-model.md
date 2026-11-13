# Canonical Domain Model — Draft v0

## DeviceIdentity
Stable logical `device_id`, product/board family, hardware revision and verified trust attributes. Never assume MAC address is a secure identity.

## Capability
`schema_version`, `feature`, support state (`SUPPORTED`, `UNSUPPORTED`, `UNKNOWN`), optional bounds and source evidence. `UNKNOWN` must not be treated as `SUPPORTED`.

## HealthSample
Monotonic timestamp, source, metric name, unit, value, validity marker and quality/error code. Missing sensors are reported without fabricated numbers.

## AIEvent
Event ID, bounded payload, source, monotonic timestamp, importance and drop policy. Hard real-time producers may never await queue admission.

## ModelManifest
Digest, format/ABI, supported target/accelerator, maximum RAM, maximum execution budget, signing metadata and provenance.

## ActionProposal
Version, authenticated principal, device audience, typed action, resource/target scope, issue time, expiry, request ID and nonce. Every action requires executor-side replay and scope checks.

## PolicyDecision
Allow/deny, stable reason code, correlation ID and rule revision. A decision is not an action and must not be confused with execution evidence.

## UpdateRecord
Board compatibility, image hash, verified signing key ID, current/target slot, staged/booted/confirmed/rolled-back state and error reason.

These are logical entities; their binary/JSON/CBOR serialization is **not frozen**. No remote management endpoint is authorized until canonical encoding, schema negotiation and security review are completed.
