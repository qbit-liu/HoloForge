"""Portable evidence bundles and explicit scientific compatibility audits.

The bundle layer is intentionally independent of any numerical solver.  It
binds an existing result record, its configuration, scientific-state metadata,
and optional artifacts with SHA-256 digests.  Compatibility is evaluated only
from declared metadata; missing fields fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import mimetypes
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from holoforge import __version__


BUNDLE_SCHEMA_VERSION = "0.4"
COMPATIBILITY_SCHEMA_VERSION = "0.4"
SAME_STATE_FAMILY = "same-state-family"

_STATE_FIELDS = (
    "model_identifier",
    "ensemble",
    "fixed_variables",
    "approximation",
    "phase_branch",
    "parameters",
    "declared_controls",
    "boundary_source_conditions",
    "conventions",
    "source_record_versions",
)
_MANIFEST_FIELDS = {
    "schema_version",
    "bundle_id",
    "command_identity",
    "holoforge_version",
    "support_level",
    "disclosure_class",
    "scientific_state",
    "model_cards",
    "acceptance",
    "software_versions",
    "scope",
    "limitations",
    "files",
    "execution",
    "scientific_payload_digest",
}
_SUPPORT_LEVELS = {
    "established-source",
    "reproduced",
    "model-extension",
    "hypothesis",
}
_ABSOLUTE_WINDOWS_PATH = re.compile(r"^[A-Za-z]:[\\/]")
_PRIVATE_KEY_MARKER = "-----BEGIN " + "PRIVATE KEY-----"
_FORBIDDEN_METADATA_KEYS = {
    "api_key",
    "credential",
    "credentials",
    "host_name",
    "hostname",
    "password",
    "secret",
    "token",
    "user_name",
    "username",
}


class EvidenceBundleError(ValueError):
    """Raised when an evidence bundle cannot be created safely."""


@dataclass(frozen=True)
class BundleAuditResult:
    """Integrity and portability result for one bundle."""

    bundle_path: str
    bundle_id: Optional[str]
    checks: Tuple[Mapping[str, Any], ...]

    @property
    def passed(self) -> bool:
        return bool(self.checks) and all(bool(check["passed"]) for check in self.checks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "audit": "evidence-bundle",
            "bundle": self.bundle_path,
            "bundle_id": self.bundle_id,
            "checks": [dict(check) for check in self.checks],
            "passed": self.passed,
            "scope": (
                "Integrity and declared-provenance audit; not scientific or "
                "empirical validation."
            ),
        }


@dataclass(frozen=True)
class CompatibilityAuditResult:
    """Declared compatibility result for two evidence bundles."""

    bundle_a: Optional[str]
    bundle_b: Optional[str]
    matched_fields: Tuple[str, ...]
    mismatches: Tuple[Mapping[str, Any], ...]
    declared_controls: Tuple[str, ...]
    control_changes: Tuple[Mapping[str, Any], ...]

    @property
    def passed(self) -> bool:
        return not self.mismatches

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": COMPATIBILITY_SCHEMA_VERSION,
            "relation": SAME_STATE_FAMILY,
            "bundle_a": self.bundle_a,
            "bundle_b": self.bundle_b,
            "matched_fields": list(self.matched_fields),
            "mismatches": [dict(item) for item in self.mismatches],
            "declared_controls": list(self.declared_controls),
            "control_changes": [dict(item) for item in self.control_changes],
            "passed": self.passed,
            "scope": (
                "Declared same-state-family compatibility; not evidence that "
                "the inputs are physically correct or scientifically useful."
            ),
        }


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for content hashing."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    """Return the SHA-256 digest of canonical JSON content."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    """Hash one file without loading it entirely into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_evidence_bundle(
    bundle_directory: Path,
    *,
    command_identity: str,
    result_record: Mapping[str, Any],
    scientific_state: Mapping[str, Any],
    model_card_references: Sequence[Mapping[str, str]],
    artifacts: Optional[Mapping[str, Path]] = None,
    created_at_utc: Optional[str] = None,
) -> Path:
    """Transactionally write a relocatable bundle without overwriting content.

    ``scientific_state`` is the complete input to the compatibility preflight.
    Controls are parameter names that may differ between otherwise compatible
    bundles.  The function rejects absolute paths in JSON metadata and records
    only paths relative to the bundle root.
    """

    if not isinstance(command_identity, str) or not command_identity.strip():
        raise EvidenceBundleError("command_identity must be non-empty")
    try:
        result = _json_copy(result_record)
        state = _json_copy(scientific_state)
        model_cards = [_json_copy(reference) for reference in model_card_references]
    except (TypeError, ValueError) as exc:
        raise EvidenceBundleError(
            "bundle inputs must contain strict finite JSON values"
        ) from exc
    _validate_result_record(result)
    _validate_state(state)
    _validate_model_card_references(model_cards)
    _reject_nonportable_metadata(result)
    _reject_nonportable_metadata(state)
    _reject_nonportable_metadata(model_cards)

    artifact_sources: List[Tuple[str, Path]] = []
    if artifacts:
        for role, source_value in sorted(artifacts.items()):
            if not isinstance(role, str) or not role.strip():
                raise EvidenceBundleError("artifact roles must be non-empty strings")
            source = Path(source_value)
            if source.is_symlink():
                raise EvidenceBundleError(f"artifact must not be symbolic: {source}")
            if not source.is_file():
                raise EvidenceBundleError(f"artifact is not a file: {source}")
            artifact_sources.append((role, source))

    directory = Path(bundle_directory)
    if not directory.name or directory in {Path("."), Path("/")}:
        raise EvidenceBundleError("bundle path must name a dedicated directory")
    if directory.is_symlink():
        raise EvidenceBundleError("bundle path must not be symbolic")
    existed_empty = directory.exists()
    if directory.exists():
        if not directory.is_dir():
            raise EvidenceBundleError("bundle path exists and is not a directory")
        if any(directory.iterdir()):
            raise EvidenceBundleError("bundle directory must be empty")
    directory.parent.mkdir(parents=True, exist_ok=True)
    working = Path(
        tempfile.mkdtemp(
            prefix=f".{directory.name}.tmp-",
            dir=str(directory.parent),
        )
    )
    committed = False
    try:
        _write_evidence_bundle_contents(
            working,
            command_identity=command_identity,
            result=result,
            state=state,
            model_cards=model_cards,
            artifact_sources=artifact_sources,
            created_at_utc=created_at_utc,
        )
        if existed_empty:
            directory.rmdir()
        try:
            working.replace(directory)
        except OSError:
            if existed_empty and not directory.exists():
                directory.mkdir()
            raise
        committed = True
    finally:
        if not committed and working.exists():
            shutil.rmtree(working)
    return directory


def _write_evidence_bundle_contents(
    directory: Path,
    *,
    command_identity: str,
    result: Mapping[str, Any],
    state: Mapping[str, Any],
    model_cards: Sequence[Mapping[str, Any]],
    artifact_sources: Sequence[Tuple[str, Path]],
    created_at_utc: Optional[str],
) -> None:
    """Write a complete bundle inside a private staging directory."""

    records_directory = directory / "records"
    artifacts_directory = directory / "artifacts"
    records_directory.mkdir(parents=True, exist_ok=True)

    configuration_record = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "command_identity": command_identity,
        "calculation_configuration": result.get(
            "configuration",
            {"comparison": result.get("comparison", command_identity)},
        ),
        "numerical_method": result.get(
            "numerical_method", result.get("numerical_validation", {})
        ),
        "scientific_state": state,
    }
    scientific_context_record = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "model_cards": model_cards,
        "benchmark_definition": _extract_benchmark_definition(result),
    }
    _reject_nonportable_metadata(configuration_record)
    _reject_nonportable_metadata(scientific_context_record)
    record_paths = (
        ("records/configuration.json", "configuration", configuration_record),
        (
            "records/model-card.json",
            "model-card-context",
            scientific_context_record,
        ),
        ("records/result.json", "result", result),
    )
    files: List[Dict[str, str]] = []
    for relative_path, role, payload in record_paths:
        target = directory / relative_path
        _write_json(target, payload)
        files.append(_file_entry(target, directory, role))

    if artifact_sources:
        artifacts_directory.mkdir(parents=True, exist_ok=True)
        for index, (role, source) in enumerate(artifact_sources):
            target = artifacts_directory / f"{index:02d}-{source.name}"
            shutil.copyfile(source, target)
            files.append(_file_entry(target, directory, f"artifact:{role}"))

    timestamp = created_at_utc
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(timestamp)
    manifest: Dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "command_identity": command_identity,
        "holoforge_version": __version__,
        "support_level": result["support_level"],
        "disclosure_class": "public",
        "scientific_state": state,
        "model_cards": model_cards,
        "acceptance": {
            "passed": result["passed"],
            "checks": result["acceptance_checks"],
        },
        "software_versions": result["software_versions"],
        "scope": _result_scope(result),
        "limitations": _result_limitations(result),
        "files": sorted(files, key=lambda item: item["path"]),
        "execution": {"created_at_utc": timestamp},
    }
    _reject_nonportable_metadata(manifest)
    scientific_digest = _scientific_payload_digest(manifest)
    manifest["bundle_id"] = f"{_slug(command_identity)}-{scientific_digest[:16]}"
    manifest["scientific_payload_digest"] = scientific_digest
    _validate_manifest_structure(manifest)
    _write_json(directory / "manifest.json", manifest)


def audit_evidence_bundle(bundle_directory: Path) -> BundleAuditResult:
    """Audit manifest structure, relative paths, file hashes, and payload hash."""

    directory = Path(bundle_directory)
    checks: List[Mapping[str, Any]] = []
    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink():
        return BundleAuditResult(
            bundle_path=str(directory),
            bundle_id=None,
            checks=(
                _check("manifest-regular-file", False, "manifest is symbolic"),
            ),
        )
    if not manifest_path.is_file():
        return BundleAuditResult(
            bundle_path=str(directory),
            bundle_id=None,
            checks=(_check("manifest-present", False, "manifest.json is missing"),),
        )

    try:
        manifest = _read_json(manifest_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return BundleAuditResult(
            bundle_path=str(directory),
            bundle_id=None,
            checks=(_check("manifest-readable", False, str(exc)),),
        )

    bundle_id = manifest.get("bundle_id")
    missing_fields = sorted(_MANIFEST_FIELDS - set(manifest))
    extra_fields = sorted(set(manifest) - _MANIFEST_FIELDS)
    checks.append(
        _check(
            "manifest-fields",
            not missing_fields and not extra_fields,
            (
                "complete"
                if not missing_fields and not extra_fields
                else "; ".join(
                    detail
                    for detail in (
                        f"missing: {', '.join(missing_fields)}"
                        if missing_fields
                        else "",
                        f"unexpected: {', '.join(extra_fields)}"
                        if extra_fields
                        else "",
                    )
                    if detail
                )
            ),
        )
    )
    checks.append(
        _check(
            "schema-version",
            manifest.get("schema_version") == BUNDLE_SCHEMA_VERSION,
            str(manifest.get("schema_version")),
        )
    )

    try:
        _validate_manifest_structure(manifest)
        structure_ok = True
        structure_detail = "manifest metadata has the required types"
    except EvidenceBundleError as exc:
        structure_ok = False
        structure_detail = str(exc)
    checks.append(
        _check("manifest-structure", structure_ok, structure_detail)
    )

    try:
        _validate_state(manifest.get("scientific_state", {}))
        state_detail = "all required compatibility fields are present"
        state_ok = True
    except EvidenceBundleError as exc:
        state_detail = str(exc)
        state_ok = False
    checks.append(_check("scientific-state", state_ok, state_detail))

    try:
        _reject_nonportable_metadata(manifest)
        portable_ok = True
        portable_detail = "metadata contains no absolute filesystem paths"
    except EvidenceBundleError as exc:
        portable_ok = False
        portable_detail = str(exc)
    checks.append(_check("portable-metadata", portable_ok, portable_detail))

    declared_paths: List[str] = []
    file_checks_ok = True
    file_details: List[str] = []
    file_entries = manifest.get("files")
    if not isinstance(file_entries, list) or not file_entries:
        file_checks_ok = False
        file_details.append("files must be a non-empty array")
        file_entries = []
    for entry in file_entries:
        if not isinstance(entry, dict):
            file_checks_ok = False
            file_details.append("file entry is not an object")
            continue
        relative_path = entry.get("path")
        if not _is_safe_relative_path(relative_path):
            file_checks_ok = False
            file_details.append(f"unsafe path: {relative_path!r}")
            continue
        if not isinstance(entry.get("role"), str) or not entry["role"]:
            file_checks_ok = False
            file_details.append(f"missing role: {relative_path!r}")
        if not isinstance(entry.get("media_type"), str) or not entry["media_type"]:
            file_checks_ok = False
            file_details.append(f"missing media type: {relative_path!r}")
        declared_paths.append(relative_path)
        target = directory / PurePosixPath(relative_path)
        if target.is_symlink() or not target.is_file():
            file_checks_ok = False
            file_details.append(f"missing or symbolic file: {relative_path}")
            continue
        expected = entry.get("sha256")
        actual = file_sha256(target)
        if expected != actual:
            file_checks_ok = False
            file_details.append(f"digest mismatch: {relative_path}")
    if len(declared_paths) != len(set(declared_paths)):
        file_checks_ok = False
        file_details.append("duplicate declared file path")
    checks.append(
        _check(
            "declared-file-integrity",
            file_checks_ok,
            "all declared hashes match" if file_checks_ok else "; ".join(file_details),
        )
    )

    actual_paths = sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path != manifest_path
    )
    extras = sorted(set(actual_paths) - set(declared_paths))
    checks.append(
        _check(
            "no-undeclared-files",
            not extras,
            "none" if not extras else f"undeclared: {', '.join(extras)}",
        )
    )

    try:
        _validate_record_consistency(directory, manifest)
        consistency_ok = True
        consistency_detail = "manifest and canonical records agree"
    except (
        EvidenceBundleError,
        KeyError,
        OSError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        consistency_ok = False
        consistency_detail = str(exc)
    checks.append(
        _check("record-consistency", consistency_ok, consistency_detail)
    )

    expected_payload_digest = manifest.get("scientific_payload_digest")
    try:
        actual_payload_digest = _scientific_payload_digest(manifest)
    except (TypeError, ValueError) as exc:
        actual_payload_digest = None
        digest_detail = str(exc)
    else:
        digest_detail = str(actual_payload_digest)
    checks.append(
        _check(
            "scientific-payload-digest",
            expected_payload_digest == actual_payload_digest,
            digest_detail,
        )
    )
    expected_bundle_id = None
    if isinstance(actual_payload_digest, str):
        expected_bundle_id = (
            f"{_slug(str(manifest.get('command_identity', 'bundle')))}-"
            f"{actual_payload_digest[:16]}"
        )
    checks.append(
        _check(
            "bundle-identity",
            bundle_id == expected_bundle_id,
            str(expected_bundle_id),
        )
    )
    return BundleAuditResult(
        bundle_path=str(directory),
        bundle_id=bundle_id if isinstance(bundle_id, str) else None,
        checks=tuple(checks),
    )


def audit_same_state_family(
    bundle_a: Path, bundle_b: Path
) -> CompatibilityAuditResult:
    """Compare two bundles using the fail-closed same-state-family relation."""

    audit_a = audit_evidence_bundle(bundle_a)
    audit_b = audit_evidence_bundle(bundle_b)
    mismatches: List[Mapping[str, Any]] = []
    if not audit_a.passed:
        mismatches.append(
            _mismatch("bundle_a", audit_a.to_dict(), None, "bundle audit failed")
        )
    if not audit_b.passed:
        mismatches.append(
            _mismatch("bundle_b", audit_b.to_dict(), None, "bundle audit failed")
        )
    if mismatches:
        return CompatibilityAuditResult(
            bundle_a=audit_a.bundle_id,
            bundle_b=audit_b.bundle_id,
            matched_fields=(),
            mismatches=tuple(mismatches),
            declared_controls=(),
            control_changes=(),
        )

    left = _read_json(Path(bundle_a) / "manifest.json")
    right = _read_json(Path(bundle_b) / "manifest.json")
    left_state = left["scientific_state"]
    right_state = right["scientific_state"]
    matched: List[str] = []

    left_controls = tuple(sorted(left_state["declared_controls"]))
    right_controls = tuple(sorted(right_state["declared_controls"]))
    if left_controls != right_controls:
        mismatches.append(
            _mismatch(
                "declared_controls",
                list(left_controls),
                list(right_controls),
                "both bundles must declare the same controls",
            )
        )
        controls: Tuple[str, ...] = ()
    else:
        controls = left_controls
        matched.append("declared_controls")

    for field in (
        "model_identifier",
        "ensemble",
        "fixed_variables",
        "approximation",
        "phase_branch",
        "boundary_source_conditions",
        "conventions",
        "source_record_versions",
    ):
        if left_state[field] == right_state[field]:
            matched.append(field)
        else:
            mismatches.append(
                _mismatch(
                    field,
                    left_state[field],
                    right_state[field],
                    "declared scientific metadata differs",
                )
            )

    control_changes: List[Mapping[str, Any]] = []
    left_parameters = left_state["parameters"]
    right_parameters = right_state["parameters"]
    for control in controls:
        if control not in left_parameters or control not in right_parameters:
            mismatches.append(
                _mismatch(
                    f"parameters.{control}",
                    left_parameters.get(control),
                    right_parameters.get(control),
                    "declared control is missing from parameters",
                )
            )
        elif left_parameters[control] != right_parameters[control]:
            control_changes.append(
                {
                    "field": f"parameters.{control}",
                    "left": left_parameters[control],
                    "right": right_parameters[control],
                }
            )

    parameter_names = sorted(set(left_parameters) | set(right_parameters))
    for name in parameter_names:
        if name in controls:
            continue
        field = f"parameters.{name}"
        if name not in left_parameters or name not in right_parameters:
            mismatches.append(
                _mismatch(
                    field,
                    left_parameters.get(name),
                    right_parameters.get(name),
                    "undeclared parameter is missing from one bundle",
                )
            )
        elif left_parameters[name] == right_parameters[name]:
            matched.append(field)
        else:
            mismatches.append(
                _mismatch(
                    field,
                    left_parameters[name],
                    right_parameters[name],
                    "undeclared parameter differs",
                )
            )

    return CompatibilityAuditResult(
        bundle_a=audit_a.bundle_id,
        bundle_b=audit_b.bundle_id,
        matched_fields=tuple(matched),
        mismatches=tuple(mismatches),
        declared_controls=controls,
        control_changes=tuple(control_changes),
    )


def _scientific_payload_digest(manifest: Mapping[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("bundle_id", None)
    payload.pop("execution", None)
    payload.pop("scientific_payload_digest", None)
    return canonical_json_sha256(payload)


def _extract_benchmark_definition(result: Mapping[str, Any]) -> Dict[str, Any]:
    fields = (
        "benchmark",
        "comparison",
        "background",
        "equations",
        "boundary_conditions",
        "solvers",
        "observables",
        "reference",
        "model_predictions",
    )
    return {field: result[field] for field in fields if field in result}


def _result_scope(result: Mapping[str, Any]) -> str:
    scope = result.get("scope")
    if isinstance(scope, str) and scope:
        return scope
    limits = result.get("interpretation_limits")
    if isinstance(limits, list) and limits:
        return " ".join(str(item) for item in limits)
    return "Declared computational evidence; not empirical validation."


def _result_limitations(result: Mapping[str, Any]) -> List[str]:
    limitations = result.get("limitations")
    if isinstance(limitations, list):
        return [str(item) for item in limitations]
    limits = result.get("interpretation_limits")
    if isinstance(limits, list):
        return [str(item) for item in limits]
    return [_result_scope(result)]


def _validate_result_record(result: Mapping[str, Any]) -> None:
    if not isinstance(result, Mapping):
        raise EvidenceBundleError("result record must be an object")
    support_level = result.get("support_level")
    if support_level not in _SUPPORT_LEVELS:
        raise EvidenceBundleError(
            "result record requires an explicit recognized support_level"
        )
    passed = result.get("passed")
    if not isinstance(passed, bool):
        raise EvidenceBundleError("result record passed state must be boolean")
    checks = result.get("acceptance_checks")
    _validate_acceptance_checks(checks, "result record")
    derived_passed = all(check["passed"] for check in checks)
    if passed != derived_passed:
        raise EvidenceBundleError(
            "result record passed state disagrees with acceptance checks"
        )
    versions = result.get("software_versions")
    if not isinstance(versions, Mapping) or not versions or not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in versions.items()
    ):
        raise EvidenceBundleError(
            "result record software_versions must contain non-empty strings"
        )
    scope = result.get("scope")
    interpretation_limits = result.get("interpretation_limits")
    if not (
        isinstance(scope, str)
        and scope.strip()
        or isinstance(interpretation_limits, list)
        and interpretation_limits
        and all(
            isinstance(item, str) and item.strip()
            for item in interpretation_limits
        )
    ):
        raise EvidenceBundleError(
            "result record requires scope or non-empty interpretation_limits"
        )


def _validate_acceptance_checks(value: Any, location: str) -> None:
    if not isinstance(value, list) or not value:
        raise EvidenceBundleError(
            f"{location} requires at least one acceptance check"
        )
    identifiers: List[str] = []
    for index, check in enumerate(value):
        if not isinstance(check, Mapping):
            raise EvidenceBundleError(
                f"{location} acceptance check {index} must be an object"
            )
        identifier = check.get("id")
        description = check.get("description")
        if not isinstance(identifier, str) or not identifier.strip():
            raise EvidenceBundleError(
                f"{location} acceptance check {index} requires an id"
            )
        if not isinstance(description, str) or not description.strip():
            raise EvidenceBundleError(
                f"{location} acceptance check {identifier!r} requires a description"
            )
        if not isinstance(check.get("passed"), bool):
            raise EvidenceBundleError(
                f"{location} acceptance check {identifier!r} must pass or fail"
            )
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise EvidenceBundleError(f"{location} acceptance check ids must be unique")


def _validate_state(state: Mapping[str, Any]) -> None:
    if not isinstance(state, Mapping):
        raise EvidenceBundleError("scientific_state must be an object")
    missing = [field for field in _STATE_FIELDS if field not in state]
    if missing:
        raise EvidenceBundleError(
            f"scientific_state is missing: {', '.join(missing)}"
        )
    extras = sorted(set(state) - set(_STATE_FIELDS))
    if extras:
        raise EvidenceBundleError(
            f"scientific_state has unexpected fields: {', '.join(extras)}"
        )
    for field in (
        "model_identifier",
        "ensemble",
        "approximation",
        "phase_branch",
    ):
        if not isinstance(state[field], str) or not state[field]:
            raise EvidenceBundleError(f"scientific_state.{field} must be non-empty")
    for field in (
        "fixed_variables",
        "parameters",
        "boundary_source_conditions",
        "conventions",
        "source_record_versions",
    ):
        if not isinstance(state[field], Mapping) or not state[field]:
            raise EvidenceBundleError(
                f"scientific_state.{field} must be a non-empty object"
            )
    controls = state["declared_controls"]
    if not isinstance(controls, list) or not all(
        isinstance(item, str) and item for item in controls
    ):
        raise EvidenceBundleError(
            "scientific_state.declared_controls must be an array of names"
        )
    if len(controls) != len(set(controls)):
        raise EvidenceBundleError("declared_controls contains duplicates")
    if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item) for item in controls):
        raise EvidenceBundleError("declared_controls contains an invalid name")


def _validate_model_card_references(references: Sequence[Mapping[str, Any]]) -> None:
    if not references:
        raise EvidenceBundleError("at least one model-card reference is required")
    for reference in references:
        required = {"id", "schema_version", "repository_path", "sha256"}
        missing = required - set(reference)
        if missing:
            raise EvidenceBundleError(
                f"model-card reference is missing: {', '.join(sorted(missing))}"
            )
        extras = set(reference) - required
        if extras:
            raise EvidenceBundleError(
                "model-card reference has unexpected fields: "
                + ", ".join(sorted(extras))
            )
        if not isinstance(reference["id"], str) or not reference["id"].strip():
            raise EvidenceBundleError("model-card id must be non-empty")
        if not isinstance(reference["schema_version"], str) or not reference[
            "schema_version"
        ].strip():
            raise EvidenceBundleError("model-card schema_version must be non-empty")
        if not _is_safe_relative_path(reference["repository_path"]):
            raise EvidenceBundleError("model-card repository_path must be relative")
        digest = reference["sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise EvidenceBundleError("model-card sha256 must be lowercase hexadecimal")


def _validate_manifest_structure(manifest: Mapping[str, Any]) -> None:
    missing = _MANIFEST_FIELDS - set(manifest)
    extras = set(manifest) - _MANIFEST_FIELDS
    if missing or extras:
        details = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if extras:
            details.append("unexpected " + ", ".join(sorted(extras)))
        raise EvidenceBundleError("manifest fields: " + "; ".join(details))
    for field in (
        "bundle_id",
        "command_identity",
        "holoforge_version",
        "support_level",
        "scope",
        "scientific_payload_digest",
    ):
        if not isinstance(manifest.get(field), str) or not manifest[field]:
            raise EvidenceBundleError(f"manifest.{field} must be non-empty")
    if manifest["support_level"] not in _SUPPORT_LEVELS:
        raise EvidenceBundleError("manifest.support_level is not recognized")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{16}", manifest["bundle_id"]):
        raise EvidenceBundleError("manifest.bundle_id has an invalid form")
    if manifest.get("disclosure_class") != "public":
        raise EvidenceBundleError("manifest.disclosure_class must be public")
    _validate_model_card_references(manifest.get("model_cards", []))
    acceptance = manifest.get("acceptance")
    if not isinstance(acceptance, Mapping):
        raise EvidenceBundleError("manifest.acceptance must be an object")
    if set(acceptance) != {"passed", "checks"}:
        raise EvidenceBundleError("manifest.acceptance has invalid fields")
    if not isinstance(acceptance.get("passed"), bool):
        raise EvidenceBundleError("manifest.acceptance.passed must be boolean")
    _validate_acceptance_checks(acceptance.get("checks"), "manifest")
    if acceptance["passed"] != all(
        check["passed"] for check in acceptance["checks"]
    ):
        raise EvidenceBundleError(
            "manifest acceptance state disagrees with acceptance checks"
        )
    versions = manifest.get("software_versions")
    if not isinstance(versions, Mapping) or not versions or not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in versions.items()
    ):
        raise EvidenceBundleError(
            "manifest.software_versions must contain non-empty strings"
        )
    limitations = manifest.get("limitations")
    if not isinstance(limitations, list) or not limitations or not all(
        isinstance(item, str) and item for item in limitations
    ):
        raise EvidenceBundleError("manifest.limitations must be non-empty strings")
    execution = manifest.get("execution")
    if not isinstance(execution, Mapping) or set(execution) != {"created_at_utc"}:
        raise EvidenceBundleError("manifest.execution timestamp is missing")
    _validate_timestamp(execution["created_at_utc"])
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) < 3:
        raise EvidenceBundleError("manifest.files must contain at least three files")
    for entry in files:
        required = {"path", "role", "media_type", "sha256"}
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise EvidenceBundleError("manifest file entry has invalid fields")
        if not _is_safe_relative_path(entry["path"]):
            raise EvidenceBundleError("manifest file path must be relative")
        if not isinstance(entry["role"], str) or not entry["role"].strip():
            raise EvidenceBundleError("manifest file role must be non-empty")
        if not isinstance(entry["media_type"], str) or not entry[
            "media_type"
        ].strip():
            raise EvidenceBundleError("manifest file media_type must be non-empty")
        if not isinstance(entry["sha256"], str) or not re.fullmatch(
            r"[0-9a-f]{64}", entry["sha256"]
        ):
            raise EvidenceBundleError("manifest file sha256 is invalid")
    digest = manifest.get("scientific_payload_digest")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise EvidenceBundleError("scientific_payload_digest is not SHA-256")


def _validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceBundleError("timestamp must be non-empty")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise EvidenceBundleError("timestamp must be ISO 8601") from exc
    if parsed.tzinfo is None:
        raise EvidenceBundleError("timestamp must include a timezone")


def _validate_record_consistency(
    directory: Path, manifest: Mapping[str, Any]
) -> None:
    """Require the canonical records to agree with their manifest envelope."""

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise EvidenceBundleError("manifest files are unavailable")
    paths_by_role: Dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        role = entry.get("role")
        path = entry.get("path")
        if role in {"configuration", "model-card-context", "result"}:
            if role in paths_by_role:
                raise EvidenceBundleError(f"duplicate canonical record role: {role}")
            if not _is_safe_relative_path(path):
                raise EvidenceBundleError(f"unsafe canonical record path: {path!r}")
            paths_by_role[str(role)] = str(path)
    required_roles = {"configuration", "model-card-context", "result"}
    missing_roles = required_roles - set(paths_by_role)
    if missing_roles:
        raise EvidenceBundleError(
            "missing canonical record roles: " + ", ".join(sorted(missing_roles))
        )

    configuration = _read_json(directory / paths_by_role["configuration"])
    model_context = _read_json(directory / paths_by_role["model-card-context"])
    result = _read_json(directory / paths_by_role["result"])
    _validate_result_record(result)

    expected_configuration = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "command_identity": manifest["command_identity"],
        "calculation_configuration": result.get(
            "configuration",
            {"comparison": result.get("comparison", manifest["command_identity"])},
        ),
        "numerical_method": result.get(
            "numerical_method", result.get("numerical_validation", {})
        ),
        "scientific_state": manifest["scientific_state"],
    }
    if configuration != expected_configuration:
        raise EvidenceBundleError(
            "configuration record disagrees with manifest or result record"
        )

    expected_model_context = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "model_cards": manifest["model_cards"],
        "benchmark_definition": _extract_benchmark_definition(result),
    }
    if model_context != expected_model_context:
        raise EvidenceBundleError(
            "model-card context disagrees with manifest or result record"
        )

    comparisons = {
        "support_level": (result["support_level"], manifest["support_level"]),
        "passed": (result["passed"], manifest["acceptance"]["passed"]),
        "acceptance_checks": (
            result["acceptance_checks"],
            manifest["acceptance"]["checks"],
        ),
        "software_versions": (
            result["software_versions"],
            manifest["software_versions"],
        ),
        "scope": (_result_scope(result), manifest["scope"]),
        "limitations": (_result_limitations(result), manifest["limitations"]),
    }
    mismatches = [
        name for name, (record_value, manifest_value) in comparisons.items()
        if record_value != manifest_value
    ]
    if mismatches:
        raise EvidenceBundleError(
            "result record disagrees with manifest: " + ", ".join(mismatches)
        )


def _reject_nonportable_metadata(value: Any, location: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized_key = str(key).strip().lower().replace("-", "_")
            if normalized_key in _FORBIDDEN_METADATA_KEYS:
                raise EvidenceBundleError(
                    f"forbidden private metadata key at {location}.{key}"
                )
            _reject_nonportable_metadata(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonportable_metadata(item, f"{location}[{index}]")
    elif isinstance(value, str):
        expanded = value.strip()
        if expanded.startswith(("/", "~/")) or _ABSOLUTE_WINDOWS_PATH.match(expanded):
            raise EvidenceBundleError(f"absolute filesystem path at {location}")
        if _PRIVATE_KEY_MARKER in value:
            raise EvidenceBundleError(f"private-key marker at {location}")


def _is_safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or value.startswith("~") or _ABSOLUTE_WINDOWS_PATH.match(value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def _file_entry(path: Path, root: Path, role: str) -> Dict[str, str]:
    relative = path.relative_to(root).as_posix()
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return {
        "path": relative,
        "role": role,
        "media_type": media_type,
        "sha256": file_sha256(path),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_json(path: Path) -> Dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle, parse_constant=_reject_json_constant)
    if not isinstance(payload, dict):
        raise json.JSONDecodeError("expected a JSON object", "", 0)
    return payload


def _reject_json_constant(value: str) -> None:
    raise json.JSONDecodeError(f"non-finite JSON constant: {value}", value, 0)


def _json_copy(value: Any) -> Any:
    return json.loads(canonical_json_bytes(value).decode("utf-8"))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "bundle"


def _check(identifier: str, passed: bool, detail: str) -> Mapping[str, Any]:
    return {"id": identifier, "passed": bool(passed), "detail": detail}


def _mismatch(
    field: str, left: Any, right: Any, reason: str
) -> Mapping[str, Any]:
    return {"field": field, "left": left, "right": right, "reason": reason}
