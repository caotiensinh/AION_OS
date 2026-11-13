"""Static meta-aion preflight and Linux-host health smoke, not a Yocto image test."""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAYER = ROOT / "meta-aion"
KAS = ROOT / "bsp/raspberrypi4-64.yml"
IMAGE = LAYER / "recipes-core/images/aion-edge-image.bb"
RECIPE = LAYER / "recipes-core/aion-health/aion-health_0.1.0.bb"
SVC = LAYER / "recipes-core/aion-health/files/aion-health.service"
SCRIPT = LAYER / "recipes-core/aion-health/files/aion-health.sh"


class MetaAionTests(unittest.TestCase):
    def test_layer_series(self):
        text = (LAYER / "conf/layer.conf").read_text()
        self.assertIn('LAYERSERIES_COMPAT_aion = "wrynose"', text)
        self.assertIn('BBFILE_COLLECTIONS += "aion"', text)
        # LAYERDIR changes as BitBake parses subsequent layers. This must
        # expand immediately to the path of meta-aion itself.
        self.assertIn('BBFILE_PATTERN_aion := "^${LAYERDIR}/"', text)
        self.assertNotIn('BBFILE_PATTERN_aion = "^${LAYERDIR}/"', text)
        self.assertIn('LAYERDEPENDS_aion = "core"', text)

    def test_kas_local_layer_and_image(self):
        text = KAS.read_text()
        self.assertIn("target: aion-edge-image", text)
        self.assertIn("  aion:\n    path: .\n    layers:\n      meta-aion:", text)
        self.assertIn('INIT_MANAGER = "systemd"', text)

    def test_image_contains_health_and_explicitly_removes_debug(self):
        text = IMAGE.read_text()
        self.assertIn('IMAGE_INSTALL:append = " aion-health"', text)
        self.assertIn('require recipes-core/images/core-image-minimal.bb', text)
        self.assertIn('IMAGE_FEATURES:remove = "debug-tweaks empty-root-password allow-empty-password allow-root-login"', text)

    def test_recipe_installs_service(self):
        text = RECIPE.read_text()
        self.assertIn("inherit systemd", text)
        self.assertIn('SYSTEMD_SERVICE:${PN} = "aion-health.service"', text)
        self.assertIn("aion-health.sh", text)

    def test_unprivileged_oneshot(self):
        text = SVC.read_text()
        for expected in ("Type=oneshot", "User=nobody", "NoNewPrivileges=yes", "ProtectSystem=strict"):
            self.assertIn(expected, text)

    def test_health_script_on_linux_host(self):
        if not pathlib.Path("/proc/uptime").exists():
            self.skipTest("procfs not present")
        result = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"^aion_health status=ok uptime_seconds=[0-9.]+ mem_total_kib=[0-9]+ mem_available_kib=[0-9]+\n$")

    def test_health_script_no_sensitive_inputs(self):
        text = SCRIPT.read_text()
        for forbidden in ("curl ", "wget ", "/etc/shadow", "/proc/cpuinfo", "ssh "):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
