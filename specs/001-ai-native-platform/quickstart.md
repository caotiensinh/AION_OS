# Reproduce the baseline

## Prerequisites
A checkout of the exact repository commit, a stable Rust toolchain compatible with `rust-version` in `Cargo.toml`, and an offline-safe development environment. The Rust prototype has **zero external crate dependencies**.

## Host verification
```sh
git rev-parse HEAD
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --all-targets
```

Record stdout/stderr, exit code, `rustc --version`, `cargo --version`, OS/architecture and the commit SHA. Failed checks are not considered PASS.

## What this does *not* verify
This baseline has no Yocto image, Zephyr firmware, board drivers, update chain, privileged executor, remote authentication, replay store or resource governor. Host unit tests cannot validate hardware deadlines, power failure recovery or secure boot.

## Evidence template
```yaml
requirement: AT-XX
verdict: TODO
git_sha: REPLACE_WITH_COMMIT
board: not_applicable
board_revision: not_applicable
toolchain: REPLACE
command: REPLACE
exit_code: null
logs: PATH_OR_URI
artifacts_sha256: {}
reviewer: UNASSIGNED
```

All hardware acceptance rows remain TODO until independently reproduced on the physical target.
