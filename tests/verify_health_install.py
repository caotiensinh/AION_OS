#!/usr/bin/env python3
"""Inspect actual Yocto do_install output from aion-health.

Checks installed files and simple host execution. The result is NOT an image,
signature, hardware safety proof, or demonstration of a booted ARM device.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


class InstallError(ValueError):
    pass


def parse_var(environment: str, key: str) -> str:
    match = re.search(rf'(?m)^{re.escape(key)}="([^"\\n]*)"$', environment)
    if not match:
        raise InstallError(f"missing expanded BitBake variable {key}")
    return match.group(1)


def verify(env_file: Path) -> dict:
    data = env_file.read_text(encoding="utf-8")
    image_root = Path(parse_var(data, "D")).resolve(strict=True)
    if not image_root.is_dir():
        raise InstallError("D does not point to an installed image directory")

    def installed(path_var: str, name: str) -> Path:
        base = parse_var(data, path_var)
        if not base.startswith("/") or ".." in Path(base).parts:
            raise InstallError(f"unsafe {path_var}")
        candidate = image_root / base.lstrip("/") / name
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(image_root) or not resolved.is_file():
            raise InstallError("installed file outside root or not a regular file")
        return resolved

    program = installed("bindir", "aion-health")
    unit = installed("systemd_system_unitdir", "aion-health.service")
    if not (program.stat().st_mode & 0o111):
        raise InstallError("health executable is not executable")

    unit_text = unit.read_text(encoding="utf-8")
    for required in (
        "Type=oneshot",
        "ExecStart=/usr/bin/aion-health",
        "User=nobody",
        "NoNewPrivileges=yes",
    ):
        if required not in unit_text:
            raise InstallError(f"missing systemd safety condition {required}")

    result = subprocess.run(
        ["sh", "-n", str(program)], capture_output=True, text=True, timeout=5, check=False
    )
    if result.returncode:
        raise InstallError(f"installed shell script syntax failed: {result.stderr[:200]}")

    run = subprocess.run(
        ["sh", str(program)], capture_output=True, text=True, timeout=5, check=False
    )
    if run.returncode or not re.fullmatch(
        r"aion_health status=ok uptime_seconds=[0-9.]+ mem_total_kib=[0-9]+ mem_available_kib=[0-9]+\n",
        run.stdout,
    ):
        raise InstallError("installed script did not produce expected host-only health snapshot")

    return {
        "scope": "bitbake_do_install_only_not_image_build",
        "binary_sha256": hashlib.sha256(program.read_bytes()).hexdigest(),
        "unit_sha256": hashlib.sha256(unit.read_bytes()).hexdigest(),
        "binary_size_bytes": program.stat().st_size,
        "unit_size_bytes": unit.stat().st_size,
        "service_nonroot_oneshot": True,
        "host_procfs_smoke_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        record = verify(args.env)
        args.out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, InstallError, UnicodeError, subprocess.SubprocessError) as e:
        print(f"HEALTH_INSTALL_FAIL: {e}", file=sys.stderr)
        return 1
    print("HEALTH_INSTALL_PASS: installed executable and systemd unit verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
