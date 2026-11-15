#![no_std]
#![forbid(unsafe_code)]
//! Deterministic, fixed-capacity event admission for untrusted AI tasks.
//!
//! Pure in-memory helper: no threads, heap allocation, inference, device I/O,
//! cryptographic verification, monotonic-clock implementation or executor.
//! External callers MUST supply trustworthy monotonic time and authorization.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Limits {
    pub max_cpu_cost_us: u32,
    pub max_payload_bytes: u32,
    pub max_ttl_ms: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Event {
    pub id: u32,
    pub created_ms: u64,
    pub deadline_ms: u64,
    pub estimated_cpu_us: u32,
    pub payload_bytes: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reject {
    InvalidTiming,
    Expired,
    InvalidCpuCost,
    CpuBudget,
    PayloadBudget,
    TtlBudget,
    Full,
}

#[derive(Debug)]
pub struct AdmissionQueue<const N: usize> {
    entries: [Option<Event>; N],
    read: usize,
    len: usize,
    limits: Limits,
    rejected: u64,
}

impl<const N: usize> AdmissionQueue<N> {
    pub const fn new(limits: Limits) -> Self {
        Self {
            entries: [None; N],
            read: 0,
            len: 0,
            limits,
            rejected: 0,
        }
    }

    pub const fn len(&self) -> usize {
        self.len
    }

    pub const fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub const fn capacity(&self) -> usize {
        N
    }

    pub const fn rejected(&self) -> u64 {
        self.rejected
    }

    /// Enqueue only bounded, non-expired work. The caller never blocks.
    pub fn try_push(&mut self, event: Event, now_ms: u64) -> Result<(), Reject> {
        let decision = self.validate(&event, now_ms).and_then(|()| {
            if self.len == N {
                Err(Reject::Full)
            } else {
                Ok(())
            }
        });
        if let Err(reason) = decision {
            self.rejected = self.rejected.saturating_add(1);
            return Err(reason);
        }
        // N > 0 because len == N was rejected, including N == 0.
        let index = (self.read + self.len) % N;
        self.entries[index] = Some(event);
        self.len += 1;
        Ok(())
    }

    pub fn pop(&mut self) -> Option<Event> {
        if self.len == 0 {
            return None;
        }
        let value = self.entries[self.read].take();
        // N > 0 whenever len > 0.
        self.read = (self.read + 1) % N;
        self.len -= 1;
        value
    }

    fn validate(&self, event: &Event, now_ms: u64) -> Result<(), Reject> {
        if event.deadline_ms <= event.created_ms || event.created_ms > now_ms {
            return Err(Reject::InvalidTiming);
        }
        if event.deadline_ms <= now_ms {
            return Err(Reject::Expired);
        }
        if event.estimated_cpu_us == 0 {
            return Err(Reject::InvalidCpuCost);
        }
        if event.estimated_cpu_us > self.limits.max_cpu_cost_us {
            return Err(Reject::CpuBudget);
        }
        if event.payload_bytes > self.limits.max_payload_bytes {
            return Err(Reject::PayloadBudget);
        }
        if event.deadline_ms - event.created_ms > self.limits.max_ttl_ms {
            return Err(Reject::TtlBudget);
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const LIMITS: Limits = Limits {
        max_cpu_cost_us: 4_000,
        max_payload_bytes: 128,
        max_ttl_ms: 50,
    };

    fn event(id: u32) -> Event {
        Event {
            id,
            created_ms: 100,
            deadline_ms: 140,
            estimated_cpu_us: 100,
            payload_bytes: 16,
        }
    }

    #[test]
    fn fifo_order_and_wraparound() {
        let mut q = AdmissionQueue::<2>::new(LIMITS);
        assert_eq!(q.try_push(event(1), 101), Ok(()));
        assert_eq!(q.try_push(event(2), 101), Ok(()));
        assert_eq!(q.pop().unwrap().id, 1);
        assert_eq!(q.try_push(event(3), 101), Ok(()));
        assert_eq!(q.pop().unwrap().id, 2);
        assert_eq!(q.pop().unwrap().id, 3);
        assert_eq!(q.pop(), None);
    }

    #[test]
    fn rejects_full_queue_without_overwriting() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        assert_eq!(q.try_push(event(1), 101), Ok(()));
        assert_eq!(q.try_push(event(2), 101), Err(Reject::Full));
        assert_eq!(q.len(), 1);
        assert_eq!(q.pop().unwrap().id, 1);
        assert_eq!(q.rejected(), 1);
    }

    #[test]
    fn zero_capacity_is_safe() {
        let mut q = AdmissionQueue::<0>::new(LIMITS);
        assert_eq!(q.try_push(event(1), 101), Err(Reject::Full));
        assert_eq!(q.pop(), None);
        assert_eq!(q.capacity(), 0);
    }

    #[test]
    fn rejects_expired_deadline() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        assert_eq!(q.try_push(event(1), 140), Err(Reject::Expired));
    }

    #[test]
    fn rejects_future_created() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        assert_eq!(q.try_push(event(1), 99), Err(Reject::InvalidTiming));
    }

    #[test]
    fn rejects_invalid_window() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.deadline_ms = e.created_ms;
        assert_eq!(q.try_push(e, 101), Err(Reject::InvalidTiming));
    }

    #[test]
    fn rejects_over_cpu_budget() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.estimated_cpu_us = 4_001;
        assert_eq!(q.try_push(e, 101), Err(Reject::CpuBudget));
    }

    #[test]
    fn rejects_zero_cpu_estimate() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.estimated_cpu_us = 0;
        assert_eq!(q.try_push(e, 101), Err(Reject::InvalidCpuCost));
    }

    #[test]
    fn rejects_over_payload_budget() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.payload_bytes = 129;
        assert_eq!(q.try_push(e, 101), Err(Reject::PayloadBudget));
    }

    #[test]
    fn rejects_over_ttl_budget() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.deadline_ms = 151;
        assert_eq!(q.try_push(e, 101), Err(Reject::TtlBudget));
    }

    #[test]
    fn boundaries_are_inclusive_below_deadline() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.deadline_ms = 150;
        e.estimated_cpu_us = LIMITS.max_cpu_cost_us;
        e.payload_bytes = LIMITS.max_payload_bytes;
        assert_eq!(q.try_push(e, 149), Ok(()));
    }

    #[test]
    fn invalid_event_does_not_consume_capacity() {
        let mut q = AdmissionQueue::<1>::new(LIMITS);
        let mut e = event(1);
        e.payload_bytes = 1000;
        assert_eq!(q.try_push(e, 101), Err(Reject::PayloadBudget));
        assert!(q.is_empty());
        assert_eq!(q.try_push(event(2), 101), Ok(()));
    }

    #[test]
    fn rejected_counter_saturates() {
        let mut q = AdmissionQueue::<0>::new(LIMITS);
        q.rejected = u64::MAX;
        assert_eq!(q.try_push(event(1), 101), Err(Reject::Full));
        assert_eq!(q.rejected(), u64::MAX);
    }

    #[test]
    fn large_deadline_does_not_overflow() {
        let mut q = AdmissionQueue::<1>::new(Limits {
            max_ttl_ms: u64::MAX,
            ..LIMITS
        });
        let e = Event {
            created_ms: 0,
            deadline_ms: u64::MAX,
            ..event(1)
        };
        assert_eq!(q.try_push(e, 0), Ok(()));
    }
}
