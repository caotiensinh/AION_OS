import unittest

from validate_kas_dump import EXPECTED, validate


class ParsedKasValidation(unittest.TestCase):
    def base(self):
        repos = {name: {"commit": sha} for name, sha in EXPECTED.items()}
        repos["aion"] = {"path": ".", "layers": {"meta-aion": None}}
        return {"machine": "raspberrypi4-64", "target": "aion-edge-image", "distro": "poky", "repos": repos}

    def test_valid_config(self):
        self.assertTrue(validate(self.base()))

    def test_wrong_machine(self):
        d = self.base()
        d["machine"] = "qemux86-64"
        with self.assertRaises(ValueError):
            validate(d)

    def test_wrong_target(self):
        d = self.base()
        d["target"] = "core-image-minimal"
        with self.assertRaises(ValueError):
            validate(d)

    def test_tampered_commit(self):
        d = self.base()
        d["repos"]["bitbake"]["commit"] = "0" * 40
        with self.assertRaises(ValueError):
            validate(d)

    def test_missing_layer(self):
        d = self.base()
        d["repos"]["aion"]["layers"] = {}
        with self.assertRaises(ValueError):
            validate(d)

    def test_new_unreviewed_repository(self):
        d = self.base()
        d["repos"]["extra"] = {"commit": "0" * 40}
        with self.assertRaises(ValueError):
            validate(d)


if __name__ == "__main__":
    unittest.main()
