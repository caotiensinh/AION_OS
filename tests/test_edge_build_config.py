"""Static, dependency-free preflight: NOT a BitBake or physical boot test."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
KAS = ROOT / "bsp" / "raspberrypi4-64.yml"

EXPECTED_REPOS = {
    "bitbake": ("openembedded/bitbake", "6e260eb6ab1631607ea414d9ff8ede1155faa5d9"),
    "core": ("openembedded/openembedded-core", "2285da08068a6d1b4a64c9a52d85a58be50e4679"),
    "meta-yocto": ("yoctoproject/meta-yocto", "79b6d87030178bed0088ad3b00aa6dfbabac37c4"),
    "meta-openembedded": ("openembedded/meta-openembedded", "c0fcd7cca3760ef24e087ac4a31b8f357cb204da"),
    "meta-raspberrypi": ("agherzan/meta-raspberrypi", "919588393f41b48cb6c5d832aa35e58a19b6762d"),
}


def inspect(text):
    # Intentionally narrow parser: immutable manifest key shape is part of the contract.
    if not re.search(r"(?m)^machine: raspberrypi4-64$", text):
        raise ValueError("target machine must be raspberrypi4-64")
    if not re.search(r"(?m)^distro: poky$", text):
        raise ValueError("target distro must be poky")
    if not re.search(r"(?m)^target: core-image-minimal$", text):
        raise ValueError("unexpected initial image")
    matches = re.findall(
        r"(?m)^  ([\w-]+):\n    url: https://github.com/([\w-]+/[\w-]+)\.git\n    commit: ([0-9a-f]{40})$",
        text,
    )
    if len(matches) != 5 or len({name for name, _, _ in matches}) != 5:
        raise ValueError("expected exactly five pinned HTTPS repositories")
    actual = {name: (url, sha) for name, url, sha in matches}
    if actual != EXPECTED_REPOS:
        raise ValueError("repository URL or SHA differs from reviewed baseline")
    if re.search(r"(?m)^\s+(?:branch|refspec|tag):", text):
        raise ValueError("floating refs are forbidden")
    if 'EXTRA_IMAGE_FEATURES = ""' not in text:
        raise ValueError("debug features not explicitly disabled")
    if re.search(r"(?im)^\s*(?:IMAGE_FEATURES|EXTRA_IMAGE_FEATURES)\s*[+?:]*=\s*[^\n]*(?:debug-tweaks|empty-root-password|allow-empty-password|allow-root-login)", text):
        raise ValueError("insecure image features requested")
    return actual


class BuildConfigTests(unittest.TestCase):
    def setUp(self):
        self.text = KAS.read_text(encoding="utf-8")

    def test_exact_pins(self):
        self.assertEqual(inspect(self.text), EXPECTED_REPOS)

    def test_reject_floating_branch(self):
        with self.assertRaises(ValueError):
            inspect(self.text + "\n    branch: master\n")

    def test_reject_tampered_sha(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("6e260eb6ab1631607ea414d9ff8ede1155faa5d9", "0" * 40))

    def test_reject_insecure_debug_features(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace('EXTRA_IMAGE_FEATURES = ""', 'EXTRA_IMAGE_FEATURES = "debug-tweaks"'))

    def test_reject_wrong_board(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("machine: raspberrypi4-64", "machine: raspberrypi3-64"))

    def test_reject_duplicate_repo_definition(self):
        with self.assertRaises(ValueError):
            inspect(self.text + "\n  core:\n    url: https://github.com/openembedded/openembedded-core.git\n    commit: 2285da08068a6d1b4a64c9a52d85a58be50e4679\n")


if __name__ == "__main__":
    unittest.main()
