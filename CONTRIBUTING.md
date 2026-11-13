# Contributing to AION OS

AION OS is experimental. Submit focused pull requests and keep safety/security claims backed by evidence.

1. Open an issue or refer to a requirement/test ID for significant work.
2. For major features, update `.specify/memory/constitution.md`, specification, plan, task list and ADRs as applicable **before** implementation.
3. Keep the smallest independently testable change; include positive, negative and boundary tests.
4. Run `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace --all-targets` for Rust changes.
5. Record exact environment, versions, commands and logs for any embedded or performance claim.
6. Never include credentials, private device data, customer configurations or undisclosed vulnerabilities in issues or commits.
7. Preserve Apache-2.0 license notices and review licenses of every dependency.

Reviewers must reject unverified claims like 'safe', 'real-time', 'secure boot', 'self-healing' or 'production-ready'. Use precise target-specific evidence instead. See [SECURITY.md](SECURITY.md).
