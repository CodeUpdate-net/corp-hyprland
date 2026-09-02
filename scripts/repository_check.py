#!/usr/bin/env python3
"""Check package directories, specs, and source metadata against the manifest."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from package_set import ManifestError, Package, PackageSet, load_manifest


SPEC_FIELD_RE = re.compile(
    r"^(Name|Version|Release|License|URL|Source0)\s*:\s*(.*?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
SOURCE_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([^/\s][^/]*)$")
RPM_SECTION_RE = re.compile(
    r"^%(package|description|prep|generate_buildrequires|build|install|check|files|changelog|pre|post|preun|postun|trigger\w*)\b"
)
OFFLINE_SECTIONS = frozenset({"prep", "build", "install", "check"})
NETWORK_COMMAND_RE = re.compile(
    r"(?:^|[;&|]\s*|\s)(?:curl|wget|git\s+(?:clone|fetch|pull|submodule)|"
    r"go\s+get|cargo\s+fetch|pip(?:3)?\s+install|npm\s+(?:ci|install)|"
    r"meson\s+wrap|conan\s+install)(?:\s|$)"
)
SCRIPTLET_RE = re.compile(r"^%(?:pre|post|preun|postun|trigger\w*)\b")


@dataclass(frozen=True)
class PackageFiles:
    directory: Path
    spec: Path
    sources: Path


def _package_files(root: Path, package: str) -> PackageFiles:
    directory = root / "packages" / package
    return PackageFiles(
        directory=directory,
        spec=directory / f"{package}.spec",
        sources=directory / "sources",
    )


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"cannot read {path}: {exc}") from exc


def _spec_fields(path: Path, text: str) -> dict[str, str]:
    fields = {name.lower(): value for name, value in SPEC_FIELD_RE.findall(text)}
    missing = sorted(
        {"name", "version", "release", "license", "url", "source0"} - fields.keys()
    )
    if missing:
        raise ManifestError(f"{path} is missing tags: {', '.join(missing)}")
    return fields


def _expand_known_macros(value: str, fields: dict[str, str]) -> str:
    replacements = {
        "%{name}": fields["name"],
        "%{version}": fields["version"],
        "%{url}": fields["url"],
    }
    for macro, replacement in replacements.items():
        value = value.replace(macro, replacement)
    return value


def _source_filename(url: str, location: Path) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise ManifestError(
            f"{location} Source0 must resolve to an HTTPS URL without credentials"
        )
    candidate = parsed.fragment.lstrip("/") if parsed.fragment else Path(parsed.path).name
    if not candidate or "/" in candidate:
        raise ManifestError(f"{location} Source0 must resolve to one archive filename")
    return candidate


def _source_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for number, raw_line in enumerate(_read(path).splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = SOURCE_LINE_RE.fullmatch(line)
        if not match:
            raise ManifestError(
                f"{path}:{number} must use '<sha256>  <filename>' format"
            )
        checksum, filename = match.groups()
        if filename in entries:
            raise ManifestError(f"{path}:{number} duplicates source {filename}")
        entries[filename] = checksum
    if not entries:
        raise ManifestError(f"{path} must contain at least one source checksum")
    return entries


def _check_no_build_network(path: Path, text: str) -> None:
    active_section: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        section = RPM_SECTION_RE.match(line)
        if section:
            name = section.group(1)
            active_section = name if name in OFFLINE_SECTIONS else None
            continue
        command = line.split("#", 1)[0]
        if active_section and NETWORK_COMMAND_RE.search(command):
            raise ManifestError(
                f"{path}:{number} runs a network command in %{active_section}"
            )


def _check_no_scriptlets(path: Path, text: str) -> None:
    for number, line in enumerate(text.splitlines(), start=1):
        if SCRIPTLET_RE.match(line):
            raise ManifestError(
                f"{path}:{number} contains a privileged RPM scriptlet"
            )


def _check_package(root: Path, package: Package) -> None:
    files = _package_files(root, package.name)
    if not files.directory.is_dir():
        raise ManifestError(f"missing package directory: {files.directory}")
    for path in (files.spec, files.sources):
        if not path.is_file():
            raise ManifestError(f"missing required package file: {path}")

    spec_text = _read(files.spec)
    fields = _spec_fields(files.spec, spec_text)
    if fields["name"] != package.name:
        raise ManifestError(
            f"{files.spec} Name {fields['name']!r} does not match {package.name!r}"
        )
    if fields["version"] != package.version:
        raise ManifestError(
            f"{files.spec} Version {fields['version']!r} does not match manifest "
            f"version {package.version!r}"
        )
    if fields["url"] != package.upstream:
        raise ManifestError(f"{files.spec} URL does not match manifest upstream")
    if not fields["license"].strip():
        raise ManifestError(f"{files.spec} License must not be empty")

    source_url = _expand_known_macros(fields["source0"], fields)
    source_name = _source_filename(source_url, files.spec)
    source_host = urlsplit(source_url).hostname
    upstream_host = urlsplit(package.upstream).hostname
    if source_host != upstream_host:
        raise ManifestError(
            f"{files.spec} Source0 host does not match manifest upstream host"
        )
    sources = _source_entries(files.sources)
    if source_name not in sources:
        raise ManifestError(f"{files.sources} has no checksum for Source0 {source_name}")
    if sources[source_name] != package.source_sha256:
        raise ManifestError(
            f"{files.sources} checksum for {source_name} does not match manifest"
        )
    _check_no_build_network(files.spec, spec_text)
    _check_no_scriptlets(files.spec, spec_text)


def check_repository(root: Path, manifest: PackageSet) -> None:
    packages_dir = root / "packages"
    actual = (
        {path.name for path in packages_dir.iterdir() if path.is_dir()}
        if packages_dir.is_dir()
        else set()
    )
    expected = set(manifest.packages)
    unlisted = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unlisted:
        raise ManifestError(
            "package directories missing from package-set.yaml: " + ", ".join(unlisted)
        )
    if missing:
        raise ManifestError("manifest packages missing directories: " + ", ".join(missing))
    for package in manifest.packages.values():
        _check_package(root, package)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    manifest_path = args.manifest or root / "package-set.yaml"
    try:
        manifest = load_manifest(manifest_path)
        check_repository(root, manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{root}: package files match {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
