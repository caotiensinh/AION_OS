# AION OS Engineering Constitution

Version 1.0 · Ratified 2026-11-13

1. **Essential function is AI-independent.** No kernel boot or safety-critical action depends on ML output.
2. **Default deny.** No model-derived command is privileged by default.
3. **Explicit budgets.** Allocate bounded memory, CPU, queue depth and deadlines per supported target.
4. **Deterministic controls first.** IRQ and hard-real-time paths never await ML or network.
5. **Offline first.** Device operation never requires a cloud service.
6. **Capability truthfulness.** Unsupported hardware or cryptographic features are declared explicitly.
7. **Update recoverability.** No release claim without target-specific signed update and recovery proof.
8. **Evidence before PASS.** Test verdicts require commit SHA, commands, outputs, environment and immutable artifacts.
9. **Public-safe engineering.** No credentials, private endpoints, device serials or proprietary data in Git.
10. **License and dependency stewardship.** Honor upstream licenses, maintain SBOM and report vulnerabilities responsibly.

All feature specs must enumerate testable user stories, FR/NFR identifiers, risks and rollback paths. Changes that weaken these tenets require a new ADR and review.
