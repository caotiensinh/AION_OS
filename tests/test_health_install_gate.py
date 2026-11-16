import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).with_name("verify_health_install.py")
spec = importlib.util.spec_from_file_location("aion_health_gate", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class HealthInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.image_root = self.root / "image"
        self.program = self.image_root / "usr/bin/aion-health"
        self.service = self.image_root / "lib/systemd/system/aion-health.service"
        self.program.parent.mkdir(parents=True)
        self.service.parent.mkdir(parents=True)
        self.program.write_text(
            "#!/bin/sh\nprintf 'aion_health status=ok uptime_seconds=1 mem_total_kib=1024 mem_available_kib=512\\n'\n"
        )
        self.program.chmod(0o755)
        self.service.write_text(
            "[Service]\nType=oneshot\nExecStart=/usr/bin/aion-health\n"
            "User=nobody\nNoNewPrivileges=yes\n"
        )
        self.env = self.root / "bitbake.env"
        self.env.write_text(
            f'D="{self.image_root}"\nbindir="/usr/bin"\n'
            'systemd_system_unitdir="/lib/systemd/system"\n'
        )

    def test_isolated_recipe_workflow_avoids_full_cross_toolchain(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/g1-health-install.yml").read_text()
        self.assertIn('bitbake -b "$GITHUB_WORKSPACE/meta-aion/recipes-core/aion-health/aion-health_0.1.0.bb" -c install', workflow)
        self.assertNotIn('bitbake -c install aion-health &&', workflow)
        self.assertIn("timeout-minutes: 22", workflow)

    def test_architecture_independent_recipe(self):
        recipe = (Path(__file__).resolve().parents[1] /
                  "meta-aion/recipes-core/aion-health/aion-health_0.1.0.bb").read_text()
        self.assertIn("inherit systemd allarch", recipe)

    def test_valid_install(self):
        data = gate.verify(self.env)
        self.assertTrue(data["service_nonroot_oneshot"])
        self.assertEqual(len(data["binary_sha256"]), 64)

    def test_missing_binary(self):
        self.program.unlink()
        with self.assertRaises((FileNotFoundError, gate.InstallError)):
            gate.verify(self.env)

    def test_missing_service(self):
        self.service.unlink()
        with self.assertRaises((FileNotFoundError, gate.InstallError)):
            gate.verify(self.env)

    def test_non_executable(self):
        self.program.chmod(0o644)
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)

    def test_privileged_service(self):
        self.service.write_text(self.service.read_text().replace("User=nobody", "User=root"))
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)

    def test_bad_script_output(self):
        self.program.write_text("#!/bin/sh\necho not-a-health-metric\n")
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)

    def test_symlink_escaping_root(self):
        self.program.unlink()
        outside = self.root / "external-script"
        outside.write_text("#!/bin/sh\necho evil\n")
        self.program.symlink_to(outside)
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)

    def test_relative_target_path_rejected(self):
        self.env.write_text(
            f'D="{self.image_root}"\nbindir="../wrong"\n'
            'systemd_system_unitdir="/lib/systemd/system"\n'
        )
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)

    def test_missing_bitbake_variable(self):
        self.env.write_text(f'D="{self.image_root}"\n')
        with self.assertRaises(gate.InstallError):
            gate.verify(self.env)


if __name__ == "__main__":
    unittest.main()
