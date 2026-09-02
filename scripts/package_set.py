#!/usr/bin/env python3
"""Validate and order the packages in package-set.yaml."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml


PACKAGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9+.-]*$")
RELEASE_SET_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.[1-9]\d*$")
VERSION_RE = re.compile(r"^[0-9][0-9A-Za-z._+~^]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
KNOWN_TIERS = frozenset({"core", "application", "compatibility"})
ROOT_FIELDS = frozenset({"schema", "release_set", "packages"})
PACKAGE_FIELDS = frozenset(
    {"upstream", "version", "source_commit", "source_sha256", "tier", "depends_on"}
)


class ManifestError(ValueError):
    """A package manifest is malformed or internally inconsistent."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ManifestError(f"mapping key must be a scalar: {key!r}") from exc
        if duplicate:
            raise ManifestError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class Package:
    name: str
    upstream: str
    version: str
    source_commit: str
    source_sha256: str
    tier: str
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class PackageSet:
    release_set: str
    packages: dict[str, Package]

    def build_waves(self) -> list[list[str]]:
        """Return deterministic topological waves for parallel builds."""
        remaining = {
            name: set(package.depends_on) for name, package in self.packages.items()
        }
        waves: list[list[str]] = []
        built: set[str] = set()

        while remaining:
            wave = sorted(
                name for name, dependencies in remaining.items() if dependencies <= built
            )
            if not wave:
                cycle = ", ".join(sorted(remaining))
                raise ManifestError(f"dependency graph contains a cycle involving: {cycle}")
            waves.append(wave)
            built.update(wave)
            for name in wave:
                del remaining[name]

        return waves

    def build_order(self) -> list[str]:
        """Return a deterministic, flattened topological order."""
        return [name for wave in self.build_waves() for name in wave]


def _expect_mapping(value: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{location} must be a mapping")
    return value


def _check_fields(
    value: Mapping[str, Any], expected: frozenset[str], location: str
) -> None:
    invalid = [key for key in value if not isinstance(key, str)]
    if invalid:
        rendered = ", ".join(repr(key) for key in invalid)
        raise ManifestError(f"{location} field names must be strings: {rendered}")
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise ManifestError(f"{location} is missing fields: {', '.join(missing)}")
    if extra:
        raise ManifestError(f"{location} has unknown fields: {', '.join(extra)}")


def _validate_upstream(value: Any, location: str) -> str:
    if not isinstance(value, str):
        raise ManifestError(f"{location} must be a string")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ManifestError(f"{location} must be an HTTPS URL without credentials")
    if parsed.fragment:
        raise ManifestError(f"{location} must not contain a fragment")
    return value


def _validate_package(name: Any, value: Any) -> Package:
    if not isinstance(name, str) or not PACKAGE_NAME_RE.fullmatch(name):
        raise ManifestError(f"invalid package name: {name!r}")

    location = f"packages.{name}"
    data = _expect_mapping(value, location)
    _check_fields(data, PACKAGE_FIELDS, location)

    version = data["version"]
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise ManifestError(
            f"{location}.version must be an RPM-compatible version string"
        )
    if version.strip().lower() in {"tbd", "todo", "unknown"} or "<" in version:
        raise ManifestError(f"{location}.version must be pinned, not a placeholder")

    checksum = data["source_sha256"]
    if not isinstance(checksum, str) or not SHA256_RE.fullmatch(checksum):
        raise ManifestError(f"{location}.source_sha256 must be 64 lowercase hex digits")

    commit = data["source_commit"]
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise ManifestError(f"{location}.source_commit must be 40 lowercase hex digits")

    tier = data["tier"]
    if not isinstance(tier, str) or tier not in KNOWN_TIERS:
        choices = ", ".join(sorted(KNOWN_TIERS))
        raise ManifestError(f"{location}.tier must be one of: {choices}")

    dependencies = data["depends_on"]
    if not isinstance(dependencies, list) or not all(
        isinstance(dependency, str) for dependency in dependencies
    ):
        raise ManifestError(f"{location}.depends_on must be a list of package names")
    if len(dependencies) != len(set(dependencies)):
        raise ManifestError(f"{location}.depends_on contains duplicates")
    if name in dependencies:
        raise ManifestError(f"{location}.depends_on must not include itself")

    return Package(
        name=name,
        upstream=_validate_upstream(data["upstream"], f"{location}.upstream"),
        version=version,
        source_commit=commit,
        source_sha256=checksum,
        tier=tier,
        depends_on=tuple(dependencies),
    )


def parse_manifest(text: str, source: str = "<string>") -> PackageSet:
    try:
        raw = yaml.load(text, Loader=UniqueKeyLoader)
    except ManifestError:
        raise
    except yaml.YAMLError as exc:
        raise ManifestError(f"invalid YAML in {source}: {exc}") from exc

    root = _expect_mapping(raw, "manifest")
    _check_fields(root, ROOT_FIELDS, "manifest")
    if root["schema"] != 1 or isinstance(root["schema"], bool):
        raise ManifestError("manifest.schema must be the integer 1")

    release_set = root["release_set"]
    if not isinstance(release_set, str) or not RELEASE_SET_RE.fullmatch(release_set):
        raise ManifestError("manifest.release_set must use YYYY-MM-DD.N format")
    date_part = release_set.rsplit(".", 1)[0]
    try:
        dt.date.fromisoformat(date_part)
    except ValueError as exc:
        raise ManifestError("manifest.release_set must contain a valid date") from exc

    raw_packages = _expect_mapping(root["packages"], "manifest.packages")
    packages = {
        name: _validate_package(name, value) for name, value in raw_packages.items()
    }

    for name, package in packages.items():
        missing = sorted(set(package.depends_on) - packages.keys())
        if missing:
            raise ManifestError(
                f"packages.{name}.depends_on refers to unknown packages: "
                + ", ".join(missing)
            )

    manifest = PackageSet(release_set=release_set, packages=packages)
    manifest.build_waves()
    return manifest


def load_manifest(path: Path) -> PackageSet:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"cannot read {path}: {exc}") from exc
    return parse_manifest(text, str(path))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest", nargs="?", type=Path, default=Path("package-set.yaml")
    )
    parser.add_argument(
        "--format", choices=("validate", "order", "waves"), default="validate"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "validate":
        count = len(manifest.packages)
        noun = "package" if count == 1 else "packages"
        print(f"{args.manifest}: valid ({count} {noun})")
    elif args.format == "order":
        for name in manifest.build_order():
            print(name)
    else:
        for number, wave in enumerate(manifest.build_waves(), start=1):
            print(f"wave {number}: {' '.join(wave)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
