# Security Policy

**Project maturity:** pre-alpha; no production deployment or security guarantees.

Please **do not open a public issue containing exploit details, keys, firmware signing secrets, customer data or live endpoints**. Use GitHub's private vulnerability-reporting feature if available, or contact the maintainer privately through an established secure channel.

Scope of concern includes parser bugs, policy bypass, replay, update signing, device identity, unsafe privilege escalation, credentials and denial-of-service. The current policy crate is a decision prototype only and must not be used as a complete authorization service.

Security requirements: default deny, no secrets in logs, no hardcoded credentials, separate AI and executor privileges, signed artifacts with a board-aware threat model, bounded resource usage, and target-specific recovery testing.

No fixed response SLA or supported release is promised at this development stage.
