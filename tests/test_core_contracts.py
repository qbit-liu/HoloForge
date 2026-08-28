"""Fail-closed tests for common scientific result contracts."""

import unittest

from holoforge.benchmarks.soft_wall_vector import (
    SoftWallConfig,
    solve_spectrum,
)
from holoforge.core.contracts import (
    AcceptanceCheck,
    BackgroundSpec,
    BenchmarkDefinition,
    BoundaryConditionSpec,
    EquationSpec,
    ObservableSpec,
    SolverSpec,
    VerificationRecord,
)


DEFINITION = BenchmarkDefinition(
    identifier="synthetic-contract-test",
    support_level="reproduced",
    background=BackgroundSpec(
        identifier="synthetic-background",
        dimension=5,
        coordinate="u",
        description="Synthetic public contract fixture.",
    ),
    equations=(
        EquationSpec(
            identifier="synthetic-equation",
            kind="ordinary differential equation",
            dependent_fields=("f",),
            expression="f' = 0",
            source_reference="synthetic fixture",
        ),
    ),
    boundary_conditions=(
        BoundaryConditionSpec(
            field="f",
            location="u = 0",
            role="normalization",
            expression="f(0) = 1",
            interpretation="Synthetic boundary value.",
        ),
    ),
    solvers=(
        SolverSpec(
            problem_type="synthetic",
            library_function="none",
            method="analytic",
            description="No numerical solve is performed.",
        ),
    ),
    observables=(
        ObservableSpec(
            identifier="constant",
            symbol="f",
            extraction="evaluate f",
            normalization="f(0) = 1",
        ),
    ),
)


def record(**updates):
    values = {
        "definition": DEFINITION,
        "configuration": {"control": 1.0},
        "numerical_method": {"route": "synthetic"},
        "results": {"value": 1.0},
        "acceptance_checks": (
            AcceptanceCheck(
                identifier="synthetic-pass",
                description="Synthetic result is exactly one.",
                passed=True,
                value=1.0,
                criterion="value == 1",
            ),
        ),
        "software_versions": {"holoforge": "test", "python": "test"},
        "scope": "Synthetic contract fixture; no scientific claim.",
    }
    values.update(updates)
    return VerificationRecord(**values)


class CoreContractTests(unittest.TestCase):
    def test_boundary_condition_preserves_physical_role(self) -> None:
        condition = BoundaryConditionSpec(
            field="phi",
            location="UV",
            role="source",
            expression="phi(0) = mu",
            interpretation="Nonzero chemical-potential source.",
        )
        self.assertEqual(condition.to_dict()["role"], "source")
        self.assertIn("Nonzero", condition.to_dict()["interpretation"])

    def test_soft_wall_uses_common_verification_envelope(self) -> None:
        payload = solve_spectrum(
            SoftWallConfig(grid_points=600), num_modes=2
        ).to_dict(tolerance=2.0e-4)

        self.assertEqual(payload["benchmark"], "soft-wall-vector")
        self.assertEqual(payload["background"]["id"], "quadratic-soft-wall-ads5")
        self.assertEqual(payload["equations"][0]["id"], "vector-schrodinger")
        self.assertEqual(len(payload["boundary_conditions"]), 2)
        self.assertEqual(
            payload["solvers"][0]["library_function"],
            "scipy.linalg.eigvalsh_tridiagonal",
        )
        self.assertTrue(payload["acceptance_checks"][0]["passed"])

    def test_empty_acceptance_checks_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            record(acceptance_checks=())

    def test_acceptance_state_must_be_boolean(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be boolean"):
            AcceptanceCheck(
                identifier="invalid-state",
                description="A string must not become truthy.",
                passed="false",
            )

    def test_acceptance_value_must_be_finite(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be finite"):
            AcceptanceCheck(
                identifier="non-finite",
                description="Non-finite evidence is invalid.",
                passed=False,
                value=float("nan"),
            )

    def test_extra_metadata_cannot_replace_canonical_state(self) -> None:
        for field in ("passed", "support_level", "configuration"):
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "reserved fields"
            ):
                record(extra={field: "replacement"})

    def test_result_payload_must_be_strict_finite_json(self) -> None:
        invalid = record(results={"value": float("inf")})
        with self.assertRaisesRegex(ValueError, "strict finite JSON"):
            invalid.to_dict()

    def test_passed_state_is_derived_from_nonempty_checks(self) -> None:
        self.assertTrue(record().passed)
        failed = record(
            acceptance_checks=(
                AcceptanceCheck(
                    identifier="synthetic-fail",
                    description="Synthetic failing control.",
                    passed=False,
                ),
            )
        )
        self.assertFalse(failed.passed)
        self.assertFalse(failed.to_dict()["passed"])


if __name__ == "__main__":
    unittest.main()
