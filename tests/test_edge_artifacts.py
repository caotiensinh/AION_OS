"""Artifact gate behavior, failure and boundary regression tests."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("verify_edge_artifacts.py")
spec = importlib.util.spec_from_file_location("aion_verify_artifacts", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ArtifactAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.deploy = self.root / "deploy"
        self.deploy.mkdir()
        self.marker = self.root / "start"
        self.marker.touch()
        self.image = self.deploy / "aion-edge-image-raspberrypi4-64.rootfs.wic.bz2"
        self.manifest = self.deploy / "aion-edge-image-raspberrypi4-64.rootfs.manifest"
        self.image.write_bytes(b"not-a-boot-image-only-test-fixture")
        self.manifest.write_text("base-files arm64 1\naion-health arm64 0.1\n")
        t = self.marker.stat().st_mtime_ns + 5_000_000_000
        os.utime(self.image, ns=(t, t))
        os.utime(self.manifest, ns=(t, t))

    def test_accepts_one_fresh_image_with_health_package(self):
        result = module.inspect(self.deploy, self.marker)
        self.assertEqual(result["image_size_bytes"], len(self.image.read_bytes()))
        self.assertEqual(len(result["image_sha256"]), 64)
        self.assertEqual(result["scope"], "artifact_only_not_boot_or_signed_update")

    def test_rejects_absent_image(self):
        self.image.unlink()
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_zero_byte_image(self):
        self.image.write_bytes(b"")
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_stale_image(self):
        old = self.marker.stat().st_mtime_ns - 5_000_000_000
        os.utime(self.image, ns=(old, old))
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_missing_health_package(self):
        self.manifest.write_text("base-files arm64 1\n")
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_fake_health_package_prefix(self):
        self.manifest.write_text("aion-health-malicious arm64 1\n")
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_absent_manifest(self):
        self.manifest.unlink()
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_accepts_symlink_alias_to_same_image(self):
        (self.deploy / "aion-edge-image-raspberrypi4-64.wic.bz2").symlink_to(self.image.name)
        result = module.inspect(self.deploy, self.marker)
        self.assertEqual(result["image"], self.image.name)

    def test_rejects_distinct_ambiguous_images(self):
        alt = self.deploy / "aion-edge-image-raspberrypi4-64.other.wic.bz2"
        alt.write_bytes(b"other")
        t = self.marker.stat().st_mtime_ns + 5_000_000_000
        os.utime(alt, ns=(t, t))
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)

    def test_rejects_symlink_escaping_deploy(self):
        self.image.unlink()
        outside = self.root / "elsewhere.wic.bz2"
        outside.write_bytes(b"image")
        self.image.symlink_to(outside)
        with self.assertRaises(module.ArtifactError):
            module.inspect(self.deploy, self.marker)


if __name__ == "__main__":
    unittest.main()
