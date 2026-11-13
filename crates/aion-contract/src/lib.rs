#![no_std]
//! AION OS wire protocol v1: fixed-size, allocation-free capability and health records.
//!
//! The frame is not authenticated or encrypted. Consumers MUST validate transport identity,
//! integrity, replay and authorization independently. This crate only parses/encodes data.

pub const FRAME_LEN: usize = 32;
pub const VERSION: u8 = 1;
const MAGIC: &[u8; 4] = b"AION";
const KIND_CAPABILITY: u8 = 1;
const KIND_HEALTH: u8 = 2;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum Support {
    Unknown = 0,
    Unsupported = 1,
    Supported = 2,
}

impl Support {
    fn parse(value: u8) -> Result<Self, DecodeError> {
        match value {
            0 => Ok(Self::Unknown),
            1 => Ok(Self::Unsupported),
            2 => Ok(Self::Supported),
            _ => Err(DecodeError::InvalidStatus),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum Validity {
    Invalid = 0,
    Valid = 1,
}

impl Validity {
    fn parse(value: u8) -> Result<Self, DecodeError> {
        match value {
            0 => Ok(Self::Invalid),
            1 => Ok(Self::Valid),
            _ => Err(DecodeError::InvalidStatus),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Capability {
    pub feature_id: u16,
    pub source_id: u16,
    pub support: Support,
    /// Feature-specific unsigned bound, zero when support is not Supported.
    pub limit: u32,
    pub observed_at_ms: u64,
    /// Zero for Supported; nonzero may explain Unsupported/Unknown.
    pub reason: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Health {
    pub metric_id: u16,
    pub source_id: u16,
    pub validity: Validity,
    /// Metric-specific signed value, zero if Invalid. Units defined per metric ID.
    pub value: i32,
    pub sampled_at_ms: u64,
    /// Zero for Valid; nonzero may explain Invalid.
    pub reason: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Record {
    Capability(Capability),
    Health(Health),
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DecodeError {
    WrongLength,
    InvalidMagic,
    UnsupportedVersion,
    UnknownKind,
    InvalidStatus,
    NonzeroReserved,
    InconsistentState,
}

fn validate(record: &Record) -> Result<(), DecodeError> {
    match record {
        Record::Capability(c) => {
            if c.support != Support::Supported && c.limit != 0 {
                return Err(DecodeError::InconsistentState);
            }
            if c.support == Support::Supported && c.reason != 0 {
                return Err(DecodeError::InconsistentState);
            }
        }
        Record::Health(h) => {
            if h.validity == Validity::Invalid && h.value != 0 {
                return Err(DecodeError::InconsistentState);
            }
            if h.validity == Validity::Valid && h.reason != 0 {
                return Err(DecodeError::InconsistentState);
            }
        }
    }
    Ok(())
}

/// Encode one validated 32-byte frame. Caller owns its buffer and no heap is used.
pub fn encode(record: &Record) -> Result<[u8; FRAME_LEN], DecodeError> {
    validate(record)?;
    let mut frame = [0_u8; FRAME_LEN];
    frame[..4].copy_from_slice(MAGIC);
    frame[4] = VERSION;
    let (kind, status, id, source, value, stamp, reason) = match record {
        Record::Capability(c) => (
            KIND_CAPABILITY,
            c.support as u8,
            c.feature_id,
            c.source_id,
            c.limit.to_le_bytes(),
            c.observed_at_ms,
            c.reason,
        ),
        Record::Health(h) => (
            KIND_HEALTH,
            h.validity as u8,
            h.metric_id,
            h.source_id,
            h.value.to_le_bytes(),
            h.sampled_at_ms,
            h.reason,
        ),
    };
    frame[5] = kind;
    frame[6] = status;
    frame[8..10].copy_from_slice(&id.to_le_bytes());
    frame[10..12].copy_from_slice(&source.to_le_bytes());
    frame[12..16].copy_from_slice(&value);
    frame[16..24].copy_from_slice(&stamp.to_le_bytes());
    frame[24..28].copy_from_slice(&reason.to_le_bytes());
    Ok(frame)
}

/// Decode a complete frame; refuse trailing bytes and any noncanonical reserved fields.
pub fn decode(frame: &[u8]) -> Result<Record, DecodeError> {
    if frame.len() != FRAME_LEN {
        return Err(DecodeError::WrongLength);
    }
    if &frame[..4] != MAGIC {
        return Err(DecodeError::InvalidMagic);
    }
    if frame[4] != VERSION {
        return Err(DecodeError::UnsupportedVersion);
    }
    if frame[7] != 0 || frame[28..].iter().any(|v| *v != 0) {
        return Err(DecodeError::NonzeroReserved);
    }
    let id = u16::from_le_bytes([frame[8], frame[9]]);
    let source = u16::from_le_bytes([frame[10], frame[11]]);
    let value = [frame[12], frame[13], frame[14], frame[15]];
    let stamp = u64::from_le_bytes([
        frame[16], frame[17], frame[18], frame[19], frame[20], frame[21], frame[22], frame[23],
    ]);
    let reason = u32::from_le_bytes([frame[24], frame[25], frame[26], frame[27]]);
    let record = match frame[5] {
        KIND_CAPABILITY => Record::Capability(Capability {
            feature_id: id,
            source_id: source,
            support: Support::parse(frame[6])?,
            limit: u32::from_le_bytes(value),
            observed_at_ms: stamp,
            reason,
        }),
        KIND_HEALTH => Record::Health(Health {
            metric_id: id,
            source_id: source,
            validity: Validity::parse(frame[6])?,
            value: i32::from_le_bytes(value),
            sampled_at_ms: stamp,
            reason,
        }),
        _ => return Err(DecodeError::UnknownKind),
    };
    validate(&record)?;
    Ok(record)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn capability() -> Record {
        Record::Capability(Capability {
            feature_id: 7,
            source_id: 2,
            support: Support::Supported,
            limit: 2048,
            observed_at_ms: 123_456,
            reason: 0,
        })
    }

    fn health() -> Record {
        Record::Health(Health {
            metric_id: 9,
            source_id: 2,
            validity: Validity::Valid,
            value: -42,
            sampled_at_ms: 987_654,
            reason: 0,
        })
    }

    #[test]
    fn capability_roundtrip() {
        let record = capability();
        assert_eq!(decode(&encode(&record).unwrap()), Ok(record));
    }

    #[test]
    fn health_negative_value_roundtrip() {
        let record = health();
        assert_eq!(decode(&encode(&record).unwrap()), Ok(record));
    }

    #[test]
    fn unknown_is_not_supported() {
        let record = Record::Capability(Capability {
            support: Support::Unknown,
            limit: 0,
            reason: 4,
            ..match capability() {
                Record::Capability(c) => c,
                _ => unreachable!(),
            }
        });
        assert_eq!(decode(&encode(&record).unwrap()), Ok(record));
    }

    #[test]
    fn invalid_health_zeroes_value() {
        let record = Record::Health(Health {
            validity: Validity::Invalid,
            value: 0,
            reason: 8,
            ..match health() {
                Record::Health(h) => h,
                _ => unreachable!(),
            }
        });
        assert_eq!(decode(&encode(&record).unwrap()), Ok(record));
    }

    #[test]
    fn refuses_short_and_trailing_frames() {
        let frame = encode(&capability()).unwrap();
        assert_eq!(decode(&frame[..31]), Err(DecodeError::WrongLength));
        let mut longer = [0_u8; 33];
        longer[..32].copy_from_slice(&frame);
        assert_eq!(decode(&longer), Err(DecodeError::WrongLength));
    }

    #[test]
    fn refuses_bad_magic_version_and_kind() {
        let frame = encode(&capability()).unwrap();
        for (index, value, expected) in [
            (0, b'X', DecodeError::InvalidMagic),
            (4, 2, DecodeError::UnsupportedVersion),
            (5, 3, DecodeError::UnknownKind),
        ] {
            let mut edited = frame;
            edited[index] = value;
            assert_eq!(decode(&edited), Err(expected));
        }
    }

    #[test]
    fn refuses_noncanonical_reserved() {
        let frame = encode(&health()).unwrap();
        for index in [7, 28, 29, 30, 31] {
            let mut edited = frame;
            edited[index] = 1;
            assert_eq!(decode(&edited), Err(DecodeError::NonzeroReserved));
        }
    }

    #[test]
    fn refuses_invalid_status_in_both_kinds() {
        for r in [capability(), health()] {
            let mut frame = encode(&r).unwrap();
            frame[6] = 3;
            assert_eq!(decode(&frame), Err(DecodeError::InvalidStatus));
        }
    }

    #[test]
    fn rejects_fabricated_unsupported_capacity() {
        let record = Record::Capability(Capability {
            support: Support::Unsupported,
            limit: 16,
            ..match capability() {
                Record::Capability(c) => c,
                _ => unreachable!(),
            }
        });
        assert_eq!(encode(&record), Err(DecodeError::InconsistentState));
        let mut raw = encode(&capability()).unwrap();
        raw[6] = Support::Unsupported as u8;
        assert_eq!(decode(&raw), Err(DecodeError::InconsistentState));
    }

    #[test]
    fn rejects_invalid_health_with_real_value() {
        let mut raw = encode(&health()).unwrap();
        raw[6] = Validity::Invalid as u8;
        assert_eq!(decode(&raw), Err(DecodeError::InconsistentState));
    }

    #[test]
    fn rejects_nonzero_reason_on_valid_data() {
        for record in [capability(), health()] {
            let mut frame = encode(&record).unwrap();
            frame[24] = 1;
            assert_eq!(decode(&frame), Err(DecodeError::InconsistentState));
        }
    }

    #[test]
    fn unsigned_limit_and_signed_value_bounds() {
        let cap = Record::Capability(Capability {
            limit: u32::MAX,
            ..match capability() {
                Record::Capability(c) => c,
                _ => unreachable!(),
            }
        });
        let h = Record::Health(Health {
            value: i32::MIN,
            ..match health() {
                Record::Health(h) => h,
                _ => unreachable!(),
            }
        });
        for r in [cap, h] {
            assert_eq!(decode(&encode(&r).unwrap()), Ok(r));
        }
    }

    #[test]
    fn fixture_is_little_endian_and_fixed_size() {
        let encoded = encode(&capability()).unwrap();
        assert_eq!(&encoded[0..8], b"AION\x01\x01\x02\x00");
        assert_eq!(&encoded[8..16], &[7, 0, 2, 0, 0, 8, 0, 0]);
        assert_eq!(&encoded[16..24], &[0x40, 0xe2, 1, 0, 0, 0, 0, 0]);
        assert_eq!(&encoded[24..32], &[0; 8]);
    }
}
