"""Guardrails for manually dispatched heavy Yocto CI workflow."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/edge-build.yml"


class WorkflowSafeguards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_manual_only(self):
        self.assertIn("  workflow_dispatch:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertNotIn("\n  pull_request:", self.text)

    def test_selfhost_required(self):
        self.assertIn("runs-on: [self-hosted, linux, x64]", self.text)

    def test_modes_are_explicit(self):
        for mode in ("          - validate", "          - parse", "          - build"):
            self.assertIn(mode, self.text)

    def test_parse_is_real_bitbake_and_gated(self):
        self.assertIn("inputs.mode == 'parse' || inputs.mode == 'build'", self.text)
        self.assertIn("bitbake -p && bitbake -e aion-edge-image >/dev/null", self.text)
        self.assertIn('min_free_kib=31457280', self.text)
        self.assertIn('min_mem_kib=8388608', self.text)

    def test_build_is_manual_and_resource_gated(self):
        self.assertIn("if: ${{ inputs.mode == 'build' }}", self.text)
        self.assertIn("min_free_kib=125829120", self.text)
        self.assertIn("min_mem_kib=16777216", self.text)
        self.assertIn('kas" build bsp/raspberrypi4-64.yml', self.text)

    def test_no_automatic_disk_write_or_image_upload(self):
        for prohibited in ("sudo dd ", "dd if=", "flashcp", "rpi-imager", "**/*.wic.bz2"):
            self.assertNotIn(prohibited, self.text)

    def test_safe_shell_and_error_propagation(self):
        self.assertGreaterEqual(self.text.count("set -euo pipefail"), 4)
        self.assertIn("aion-bitbake-parse.log", self.text)
        self.assertIn("concurrency:", self.text)


if __name__ == "__main__":
    unittest.main()
