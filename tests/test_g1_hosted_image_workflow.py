"""Guard a real hosted image-build experiment from accidental paid/destructive work."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/g1-hosted-image.yml"
MANIFEST = ROOT / "bsp/raspberrypi4-64.yml"


class HostedImageWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        cls.manifest = MANIFEST.read_text()

    def test_standard_free_runner_only(self):
        self.assertIn("runs-on: ubuntu-22.04", self.workflow)
        self.assertNotIn("runs-on: [self-hosted", self.workflow)

    def test_no_push_or_schedule_triggers(self):
        self.assertIn("  workflow_dispatch:", self.workflow)
        self.assertIn("  pull_request:", self.workflow)
        self.assertNotIn("\n  push:", self.workflow)
        self.assertNotIn("\n  schedule:", self.workflow)

    def test_fork_untrusted_changes_do_not_execute_build(self):
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", self.workflow)
        self.assertIn("github.head_ref == 'feat/g1-hosted-image-build'", self.workflow)
        self.assertIn("contents: read", self.workflow)

    def test_resource_and_concurrency_guards(self):
        self.assertIn('78643200', self.workflow)
        self.assertIn('12582912', self.workflow)
        self.assertIn('timeout-minutes: 320', self.workflow)
        self.assertIn('concurrency:', self.workflow)

    def test_build_and_verify_must_both_pass(self):
        self.assertIn('kas" build bsp/raspberrypi4-64.yml', self.workflow)
        self.assertIn('verify_edge_artifacts.py', self.workflow)
        self.assertIn('if: ${{ success() }}', self.workflow)
        self.assertIn('if-no-files-found: error', self.workflow)

    def test_real_image_is_preserved_for_review(self):
        self.assertIn('steps.gate.outputs.image_path', self.workflow)
        self.assertIn('aion-image-evidence.json', self.workflow)
        self.assertIn('retention-days: 7', self.workflow)

    def test_no_disk_flashing_or_privileged_host_changes(self):
        for prohibited in ("sudo dd ", "dd if=", "flashcp", "rpi-imager", "sysctl -w", "apparmor_parser", "force-push"):
            self.assertNotIn(prohibited, self.workflow)

    def test_constrained_bitbake_resource_policy(self):
        self.assertIn('BB_NUMBER_THREADS = "2"', self.manifest)
        self.assertIn('PARALLEL_MAKE = "-j 2"', self.manifest)
        self.assertIn('INHERIT += "rm_work"', self.manifest)


if __name__ == "__main__":
    unittest.main()
