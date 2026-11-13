# Policy Decision Contract v0 (prototype)

A proposal has **principal**, **device identity**, **action**, **expiry** and **request ID**. A rule binds a principal/device/action and a maximum TTL. Only known typed actions are supported. A match is a necessary but **not sufficient** precondition for execution.

## Current Rust prototype
`PolicyEngine::evaluate(&Proposal, now)` returns `Decision::Allow` or `Decision::Deny(DenyReason)`; there are no side effects. Unknown action, missing or mismatched identity, expired proposal, invalid TTL and absent rule are denied.

## Intentionally not implemented
Cryptographic authentication, persisted anti-replay, monotonic clock synchronization, audit emission, serialization limits, privileged execution and platform-specific enforcement. These must be completed before a device accepts remotely or model-generated commands.

## Future wire contract requirements
Versioned canonical envelope; bounded request size; authenticated principal; audience-bound device identity; monotonic anti-replay nonce; deadline/expiry; explicitly scoped action; deterministic reject reasons; digest-linked audit. Unknown major versions and fields carrying privilege are rejected.
