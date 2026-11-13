#!/usr/bin/env python3
"""Gate AION Edge builds on real image artifacts, not merely BitBake exit status.

No disk modification or privileged action. Assumes the image producer is already
trusted; SHA-256 here is an integrity inventory, NOT a signature or secure boot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


class ArtifactError(ValueError):
    pass


def inspect(deploy: Path, marker: Path) -> dict:
    deploy = deploy.resolve(strict=True)
    if not deploy.is_dir():
        raise ArtifactError("image deploy directory is not a directory")
    threshold = marker.stat().st_mtime_ns
    images = []
    for candidate in sorted(deploy.glob("aion-edge-image-*.wic.bz2")):
        # Do not accept dangling symlinks or files outside the deployment tree.
        try:
            image = candidate.resolve(strict=True)
        except FileNotFoundError:
            continue
        if not image.is_relative_to(deploy) or not image.is_file():
            raise ArtifactError("image resolves outside deployment directory")
        if image.stat().st_size == 0 or image.stat().st_mtime_ns < threshold:
            continue
        images.append(image)
    if not images:
        raise ArtifactError("no fresh nonempty aion-edge-image *.wic.bz2")
    # A single physical image may have both symlink and real-filename aliases.
    images = list(dict.fromkeys(images))
    if len(images) != 1:
        raise ArtifactError("multiple distinct fresh AION images; ambiguous build output")

    manifests = []
    for path in sorted(deploy.glob("aion-edge-image-*.manifest")):
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(deploy):
            raise ArtifactError("manifest resolves outside deployment directory")
        if resolved.stat().st_mtime_ns < threshold:
            continue
        lines = resolved.read_text(encoding="utf-8").splitlines()
        if any(line.split()[:1] == ["aion-health"] for line in lines):
            manifests.append(resolved)
    if not manifests:
        raise ArtifactError("no fresh image manifest listing aion-health")
    manifest = list(dict.fromkeys(manifests))[-1]

    def digest(path: Path) -> str:
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
        return sha.hexdigest()

    return {
        "schema_version": 1,
        "image": images[0].name,
        "image_size_bytes": images[0].stat().st_size,
        "image_sha256": digest(images[0]),
        "manifest": manifest.name,
        "manifest_sha256": digest(manifest),
        "aion_health_package_present": True,
        "scope": "artifact_only_not_boot_or_signed_update",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy", type=Path, required=True)
    parser.add_argument("--build-start-marker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        record = inspect(args.deploy, args.build_start_marker)
        args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ArtifactError) as exc:
        print(f"ARTIFACT_GATE_FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"ARTIFACT_GATE_PASS: {record['image']} ({record['image_size_bytes']} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
