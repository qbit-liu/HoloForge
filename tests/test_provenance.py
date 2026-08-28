"""Tests for privacy-safe numerical runtime provenance."""

import re
import unittest

from holoforge.core.provenance import runtime_versions


class RuntimeProvenanceTests(unittest.TestCase):
    def test_runtime_fingerprint_is_complete_and_stable(self) -> None:
        first = runtime_versions()
        second = runtime_versions()
        for field in (
            "holoforge",
            "python",
            "python_implementation",
            "byteorder",
            "platform_system",
            "platform_machine",
            "numpy",
            "scipy",
            "numerical_build_sha256",
        ):
            self.assertIn(field, first)
            self.assertIsInstance(first[field], str)
            self.assertTrue(first[field])
        self.assertEqual(first, second)
        self.assertRegex(first["numerical_build_sha256"], r"^[0-9a-f]{64}$")

    def test_runtime_fingerprint_contains_no_private_identity_fields(self) -> None:
        provenance = runtime_versions()
        combined = " ".join(provenance).lower()
        for forbidden in (
            "username",
            "hostname",
            "password",
            "secret",
            "token",
            "credential",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertFalse(
            any(
                re.match(r"^(?:/|~|[A-Za-z]:[\\/])", value)
                for value in provenance.values()
            )
        )


if __name__ == "__main__":
    unittest.main()
