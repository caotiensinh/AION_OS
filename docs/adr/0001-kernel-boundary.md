# ADR-0001: AI stays outside privileged kernel paths

**Status:** Accepted for specification baseline · 2026-11-13

**Context:** ML inference is nondeterministic in duration, can exhaust memory and processes untrusted model and sensor data.

**Decision:** Keep scheduling, essential I/O, real-time paths and safety mechanisms independent of AI. AI runs as a resource-constrained service or lower-priority RTOS task and may only propose bounded actions. A separate, default-deny policy interface controls authorization.

**Consequences:** AION can reuse mature kernels, lower risk of scheduler starvation, and run without a model. Users do not get 'AI in kernel' execution privileges; the product is AI-native at the OS service and management architecture boundary.

**Review trigger:** measured and reproducible evidence of a kernel-level limitation with explicit security and timing analysis.
