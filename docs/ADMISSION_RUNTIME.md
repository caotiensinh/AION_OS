# AION AI event admission — portable prototype

**Status:** host-tested pure `no_std` Rust library, not integrated with a scheduler, kernel, systemd service, AI model or device executor.

`aion-admission` provides a fixed-capacity FIFO ring buffer with explicit limits for per-event estimated CPU time, payload bytes and event TTL. Admission is nonblocking and never allocates on the heap. Expired, future-issued, over-budget and full-queue requests are rejected, with a saturating rejected-event counter. A zero-capacity queue rejects safely.

## Security and scheduling boundaries
- All events and estimates are **untrusted inputs**; a real system must measure runtime usage and impose cgroup/RTOS preemption independently.
- `estimated_cpu_us` is an **admission estimate**, never a guarantee of CPU enforcement.
- Caller must supply a trusted monotonic clock; this prototype does not check signatures, replay or device identity.
- Queue order is FIFO, not a realtime scheduler; safety-critical paths must not block on AI or queue operations.
- No OS integration, target-CPU measurements, or Cortex-M runtime acceptance is claimed.

## Host and target checks
```sh
cargo test -p aion-admission --all-targets
cargo clippy -p aion-admission --all-targets -- -D warnings
rustup target add thumbv7em-none-eabihf
cargo check -p aion-admission --target thumbv7em-none-eabihf --release
```

Only a persisted CI PASS proves the target compile, not that firmware was flashed or ran on a MCU. This is a **T010 prototype sub-task**; T010 remains TODO until integrated with real inference admission, observation and overload tests.
