#!/usr/bin/env python3
"""AION OS experimental detached Ed25519 image-manifest signer/verifier.

This authenticates a file with an explicitly trusted key, but it is NOT secure
boot, rollback prevention, measured boot, a flash utility, or a device update.
Do not commit private signing keys or production material.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


BOARD = "raspberrypi4-64"
SCHEMA_VERSION = 1
FIELDS = frozenset({
    "algorithm", "schema_version", "board", "version", "image",
    "image_size_bytes", "image_sha256", "build_sha", "signer",
})


class ManifestError(ValueError):
    pass


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError("duplicate manifest JSON field")
        result[key] = value
    return result


def canonical_bytes(data):
    if type(data) is not dict or set(data) != FIELDS:
        raise ManifestError("missing or unknown manifest field")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ManifestError("unsupported manifest schema")
    if data["algorithm"] != "Ed25519" or data["board"] != BOARD:
        raise ManifestError("unsupported signing algorithm or board")
    for key, pattern in (
        ("version", r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?"),
        ("build_sha", r"[a-f0-9]{40}"),
        ("image_sha256", r"[a-f0-9]{64}"),
        ("signer", r"[A-Za-z0-9._-]{1,48}"),
        ("image", r"[A-Za-z0-9._+-]{1,200}\.wic\.bz2"),
    ):
        if type(data[key]) is not str or not re.fullmatch(pattern, data[key]):
            raise ManifestError(f"invalid {key}")
    if Path(data["image"]).name != data["image"]:
        raise ManifestError("manifest image must be a filename")
    if type(data["image_size_bytes"]) is not int or not (0 < data["image_size_bytes"] < (1 << 50)):
        raise ManifestError("invalid image size")
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def file_digest(path):
    if not path.is_file():
        raise ManifestError("image is not a readable regular file")
    sha = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            size += len(chunk)
            sha.update(chunk)
    if size == 0:
        raise ManifestError("cannot authenticate an empty image")
    return sha.hexdigest(), size


def _openssl(args):
    try:
        result = subprocess.run(
            ["openssl", "pkeyutl", *args],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ManifestError("OpenSSL Ed25519 operation unavailable") from exc
    if result.returncode:
        raise ManifestError("OpenSSL Ed25519 signing or verification failed")


def _temp_path(parent):
    fd, name = tempfile.mkstemp(prefix=".aion-manifest-", dir=parent)
    os.close(fd)
    return Path(name)


def sign(image, version, build_sha, signer_id, private_key, manifest, signature):
    image = Path(image)
    manifest = Path(manifest)
    signature = Path(signature)
    if manifest == signature or manifest.resolve() == signature.resolve():
        raise ManifestError("manifest and signature paths must be distinct")
    if not Path(private_key).is_file():
        raise ManifestError("private signing key not available")
    digest, size = file_digest(image)
    record = {
        "algorithm": "Ed25519",
        "schema_version": SCHEMA_VERSION,
        "board": BOARD,
        "version": version,
        "image": image.name,
        "image_size_bytes": size,
        "image_sha256": digest,
        "build_sha": build_sha,
        "signer": signer_id,
    }
    payload = canonical_bytes(record)
    if not manifest.parent.is_dir() or not signature.parent.is_dir():
        raise ManifestError("output directory missing")
    temp_manifest = _temp_path(manifest.parent)
    temp_sig = _temp_path(signature.parent)
    try:
        temp_manifest.write_bytes(payload)
        _openssl(["-sign", "-rawin", "-inkey", str(private_key), "-in", str(temp_manifest), "-out", str(temp_sig)])
        if len(temp_sig.read_bytes()) != 64:
            raise ManifestError("Ed25519 signature must be 64 bytes")
        os.replace(temp_manifest, manifest)
        os.replace(temp_sig, signature)
    finally:
        temp_manifest.unlink(missing_ok=True)
        temp_sig.unlink(missing_ok=True)
    return record


def verify(image, manifest, signature, public_key, expected_signer, expected_board=BOARD):
    image = Path(image)
    manifest = Path(manifest)
    signature = Path(signature)
    if not Path(public_key).is_file():
        raise ManifestError("trusted public key unavailable")
    raw = manifest.read_bytes()
    if not (0 < len(raw) <= 4096):
        raise ManifestError("invalid manifest length")
    try:
        record = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError("malformed manifest JSON") from exc
    if canonical_bytes(record) != raw:
        raise ManifestError("noncanonical manifest JSON")
    if expected_board != BOARD or record["board"] != expected_board:
        raise ManifestError("board mismatch")
    if record["signer"] != expected_signer:
        raise ManifestError("signer identity mismatch")
    if record["image"] != image.name:
        raise ManifestError("image filename mismatch")
    digest, size = file_digest(image)
    if digest != record["image_sha256"] or size != record["image_size_bytes"]:
        raise ManifestError("image hash or length mismatch")
    if len(signature.read_bytes()) != 64:
        raise ManifestError("signature length invalid")
    _openssl([
        "-verify", "-rawin", "-pubin", "-inkey", str(public_key),
        "-in", str(manifest), "-sigfile", str(signature),
    ])
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("sign")
    check = sub.add_parser("verify")
    for p in (create, check):
        p.add_argument("--image", type=Path, required=True)
        p.add_argument("--manifest", type=Path, required=True)
        p.add_argument("--signature", type=Path, required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--build-sha", required=True)
    create.add_argument("--signer", required=True)
    create.add_argument("--private-key", type=Path, required=True)
    check.add_argument("--expected-signer", required=True)
    check.add_argument("--expected-board", default=BOARD)
    check.add_argument("--public-key", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "sign":
            record = sign(
                args.image, args.version, args.build_sha, args.signer,
                args.private_key, args.manifest, args.signature,
            )
        else:
            record = verify(
                args.image, args.manifest, args.signature, args.public_key,
                args.expected_signer, args.expected_board,
            )
    except (ManifestError, OSError) as exc:
        print(f"AION_MANIFEST_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"AION_MANIFEST_{'SIGNED' if args.command == 'sign' else 'VERIFIED'}: {record['image_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
