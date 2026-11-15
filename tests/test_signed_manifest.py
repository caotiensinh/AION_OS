"""Ed25519 manifest signature and integrity behavior with temporary test keys."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools/aion_image_manifest.py"
spec = importlib.util.spec_from_file_location("aion_manifest", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SignedManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p = Path(self.temp.name)
        self.key = self.p / "private.pem"
        self.pub = self.p / "pub.pem"
        self.image = self.p / "aion-edge-image-test.wic.bz2"
        self.manifest = self.p / "image.manifest.json"
        self.signature = self.p / "image.manifest.sig"
        self.image.write_bytes(b"fixture-not-real-firmware")
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(self.key)],
            capture_output=True, check=True, timeout=10,
        )
        subprocess.run(
            ["openssl", "pkey", "-in", str(self.key), "-pubout", "-out", str(self.pub)],
            capture_output=True, check=True, timeout=10,
        )

    def signed(self):
        return m.sign(self.image, "0.1.0", "a" * 40, "dev-aion", self.key, self.manifest, self.signature)

    def verified(self):
        return m.verify(self.image, self.manifest, self.signature, self.pub, "dev-aion")

    def test_roundtrip_signature(self):
        data = self.signed()
        self.assertEqual(self.verified(), data)
        self.assertEqual(self.signature.stat().st_size, 64)

    def test_image_tampering_detected(self):
        self.signed()
        self.image.write_bytes(b"changed-payload")
        with self.assertRaises(m.ManifestError):
            self.verified()

    def test_signature_tampering_detected(self):
        self.signed()
        bad = bytearray(self.signature.read_bytes())
        bad[0] ^= 1
        self.signature.write_bytes(bad)
        with self.assertRaises(m.ManifestError):
            self.verified()

    def test_wrong_key_detected(self):
        self.signed()
        other = self.p / "other.pem"
        pub = self.p / "other-pub.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(other)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(other), "-pubout", "-out", str(pub)], check=True, capture_output=True)
        with self.assertRaises(m.ManifestError):
            m.verify(self.image, self.manifest, self.signature, pub, "dev-aion")

    def test_signer_mismatch_detected(self):
        self.signed()
        with self.assertRaises(m.ManifestError):
            m.verify(self.image, self.manifest, self.signature, self.pub, "untrusted")

    def test_board_mismatch_detected(self):
        self.signed()
        with self.assertRaises(m.ManifestError):
            m.verify(self.image, self.manifest, self.signature, self.pub, "dev-aion", "raspberrypi3-64")

    def test_duplicate_field_rejected(self):
        self.signed()
        raw = self.manifest.read_text()
        self.manifest.write_text(raw.replace('"algorithm":"Ed25519",', '"algorithm":"Ed25519","algorithm":"Ed25519",'))
        with self.assertRaises(m.ManifestError):
            self.verified()

    def test_noncanonical_manifest_rejected(self):
        self.signed()
        data = json.loads(self.manifest.read_text())
        self.manifest.write_text(json.dumps(data, indent=2))
        with self.assertRaises(m.ManifestError):
            self.verified()

    def test_unknown_field_rejected(self):
        self.signed()
        data = json.loads(self.manifest.read_text())
        data["root_shell"] = True
        self.manifest.write_bytes((json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode())
        with self.assertRaises(m.ManifestError):
            self.verified()

    def test_zero_length_image_not_signed(self):
        self.image.write_bytes(b"")
        with self.assertRaises(m.ManifestError):
            self.signed()

    def test_invalid_version_rejected(self):
        with self.assertRaises(m.ManifestError):
            m.sign(self.image, "latest", "a" * 40, "dev-aion", self.key, self.manifest, self.signature)

    def test_invalid_git_commit_rejected(self):
        with self.assertRaises(m.ManifestError):
            m.sign(self.image, "0.1.0", "not-a-revision", "dev-aion", self.key, self.manifest, self.signature)

    def test_wrong_firmware_filename_rejected(self):
        self.signed()
        renamed = self.p / "other.wic.bz2"
        renamed.write_bytes(self.image.read_bytes())
        with self.assertRaises(m.ManifestError):
            m.verify(renamed, self.manifest, self.signature, self.pub, "dev-aion")

    def test_missing_trusted_key_is_rejected(self):
        self.signed()
        with self.assertRaises(m.ManifestError):
            m.verify(self.image, self.manifest, self.signature, self.p / "missing.pub", "dev-aion")


if __name__ == "__main__":
    unittest.main()
