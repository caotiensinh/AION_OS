//! AION OS host-side policy decision prototype.
//!
//! This crate neither authenticates principals nor executes actions. An OS
//! executor MUST independently enforce authorization, replay protection,
//! device identity, bounded payloads and capability-specific safety checks.

/// Small closed action set. Unrecognized actions cannot be represented.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Action {
    PauseInference,
    ResumeInference,
    ReadHealth,
}

/// Proposal fields must originate from an authenticated, bounded transport.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Proposal<'a> {
    pub request_id: &'a str,
    pub principal: &'a str,
    pub device_id: &'a str,
    pub action: Action,
    pub issued_at: u64,
    pub expires_at: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Rule<'a> {
    pub principal: &'a str,
    pub device_id: &'a str,
    pub action: Action,
    pub max_ttl_secs: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DenyReason {
    EmptyIdentity,
    InvalidTimeWindow,
    Expired,
    Unauthorized,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    Allow,
    Deny(DenyReason),
}

/// Pure decision service. No I/O, caching, implicit allow or device action.
#[derive(Debug, Clone)]
pub struct PolicyEngine<'a> {
    rules: &'a [Rule<'a>],
}

impl<'a> PolicyEngine<'a> {
    pub const fn new(rules: &'a [Rule<'a>]) -> Self {
        Self { rules }
    }

    pub fn evaluate(&self, proposal: &Proposal<'_>, now: u64) -> Decision {
        if proposal.request_id.is_empty()
            || proposal.principal.is_empty()
            || proposal.device_id.is_empty()
        {
            return Decision::Deny(DenyReason::EmptyIdentity);
        }

        // Reject zero-duration, reversed or not-yet-valid windows.
        if proposal.expires_at <= proposal.issued_at || now < proposal.issued_at {
            return Decision::Deny(DenyReason::InvalidTimeWindow);
        }
        if now >= proposal.expires_at {
            return Decision::Deny(DenyReason::Expired);
        }

        // Zero means no permission: a rule can never authorize a zero TTL.
        let allowed = self.rules.iter().any(|r| {
            r.principal == proposal.principal
                && r.device_id == proposal.device_id
                && r.action == proposal.action
                && r.max_ttl_secs > 0
                && proposal.expires_at - proposal.issued_at <= r.max_ttl_secs
        });
        if allowed {
            Decision::Allow
        } else {
            Decision::Deny(DenyReason::Unauthorized)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn proposal<'a>() -> Proposal<'a> {
        Proposal {
            request_id: "req-1",
            principal: "device-agent",
            device_id: "edge-1",
            action: Action::PauseInference,
            issued_at: 100,
            expires_at: 120,
        }
    }

    fn allowed_rules<'a>() -> [Rule<'a>; 1] {
        [Rule {
            principal: "device-agent",
            device_id: "edge-1",
            action: Action::PauseInference,
            max_ttl_secs: 30,
        }]
    }

    #[test]
    fn default_deny() {
        assert_eq!(
            PolicyEngine::new(&[]).evaluate(&proposal(), 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
    }

    #[test]
    fn explicit_match_allows() {
        let rules = allowed_rules();
        assert_eq!(
            PolicyEngine::new(&rules).evaluate(&proposal(), 110),
            Decision::Allow
        );
    }

    #[test]
    fn rejects_wrong_principal_device_and_action() {
        let rules = allowed_rules();
        let engine = PolicyEngine::new(&rules);
        let mut p = proposal();
        p.principal = "intruder";
        assert_eq!(
            engine.evaluate(&p, 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
        p = proposal();
        p.device_id = "edge-2";
        assert_eq!(
            engine.evaluate(&p, 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
        p = proposal();
        p.action = Action::ResumeInference;
        assert_eq!(
            engine.evaluate(&p, 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
    }

    #[test]
    fn rejects_expiry_and_future_issued_time() {
        let rules = allowed_rules();
        let engine = PolicyEngine::new(&rules);
        assert_eq!(
            engine.evaluate(&proposal(), 120),
            Decision::Deny(DenyReason::Expired)
        );
        assert_eq!(
            engine.evaluate(&proposal(), 99),
            Decision::Deny(DenyReason::InvalidTimeWindow)
        );
    }

    #[test]
    fn rejects_invalid_windows_and_overlong_ttl() {
        let rules = allowed_rules();
        let engine = PolicyEngine::new(&rules);
        let mut p = proposal();
        p.expires_at = 100;
        assert_eq!(
            engine.evaluate(&p, 100),
            Decision::Deny(DenyReason::InvalidTimeWindow)
        );
        p.expires_at = 131;
        assert_eq!(
            engine.evaluate(&p, 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
    }

    #[test]
    fn rejects_missing_identity_and_zero_ttl_rules() {
        let mut p = proposal();
        p.request_id = "";
        let rules = allowed_rules();
        assert_eq!(
            PolicyEngine::new(&rules).evaluate(&p, 110),
            Decision::Deny(DenyReason::EmptyIdentity)
        );
        let zero_rules = [Rule {
            max_ttl_secs: 0,
            ..rules[0].clone()
        }];
        assert_eq!(
            PolicyEngine::new(&zero_rules).evaluate(&proposal(), 110),
            Decision::Deny(DenyReason::Unauthorized)
        );
    }

    #[test]
    fn boundary_at_issue_time_allowed() {
        let rules = allowed_rules();
        assert_eq!(
            PolicyEngine::new(&rules).evaluate(&proposal(), 100),
            Decision::Allow
        );
    }
}
