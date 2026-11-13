#!/usr/bin/env python3
"""Validate the parsed kas JSON. This does not perform BitBake parsing or build."""
import json
import pathlib
import sys

EXPECTED = {
    "bitbake": "6e260eb6ab1631607ea414d9ff8ede1155faa5d9",
    "core": "2285da08068a6d1b4a64c9a52d85a58be50e4679",
    "meta-yocto": "79b6d87030178bed0088ad3b00aa6dfbabac37c4",
    "meta-openembedded": "c0fcd7cca3760ef24e087ac4a31b8f357cb204da",
    "meta-raspberrypi": "919588393f41b48cb6c5d832aa35e58a19b6762d",
}


def validate(doc):
    if doc.get("machine") != "raspberrypi4-64":
        raise ValueError("wrong MACHINE")
    if doc.get("target") != "aion-edge-image":
        raise ValueError("wrong image target")
    if doc.get("distro") != "poky":
        raise ValueError("wrong distro")
    repos = doc.get("repos")
    if not isinstance(repos, dict) or set(repos) != set(EXPECTED) | {"aion"}:
        raise ValueError("unexpected repositories")
    for name, commit in EXPECTED.items():
        if repos[name].get("commit") != commit:
            raise ValueError(f"unpinned or unexpected SHA: {name}")
    local = repos["aion"]
    if local.get("path") != "." or "meta-aion" not in local.get("layers", {}):
        raise ValueError("local AION layer not properly configured")
    return True


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: validate_kas_dump.py expanded-kas.json")
    doc = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
    validate(doc)
    print("PASS: kas expanded manifest structure and immutable source pins")


if __name__ == "__main__":
    main(sys.argv)
