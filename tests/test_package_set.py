from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from package_set import ManifestError, parse_manifest  # noqa: E402
from repository_check import check_repository  # noqa: E402


CHECKSUM_A = "a" * 64
CHECKSUM_B = "b" * 64
CHECKSUM_C = "c" * 64
COMMIT_A = "1" * 40


def manifest(packages: str = "{}") -> str:
    return (
        "schema: 1\n"
        'release_set: "2026-09-01.1"\n'
        f"packages: {packages}\n"
    )


def package(
    name: str,
    checksum: str,
    dependencies: str = "[]",
    tier: str = "core",
) -> str:
    return textwrap.indent(
        textwrap.dedent(
            f"""\
            {name}:
              upstream: https://github.com/hyprwm/{name}
              version: "1.2.3"
              source_commit: "{COMMIT_A}"
              source_sha256: "{checksum}"
              tier: {tier}
              depends_on: {dependencies}
            """
        ),
        "  ",
    ).rstrip()


class ParseManifestTests(unittest.TestCase):
    def test_empty_bootstrap_manifest_is_valid(self) -> None:
        parsed = parse_manifest(manifest())
        self.assertEqual([], parsed.build_waves())

    def test_build_waves_are_deterministic(self) -> None:
        packages = "\n" + "\n".join(
            [
                package("hyprland", CHECKSUM_C, "[aquamarine, hyprutils]"),
                package("hyprutils", CHECKSUM_A),
                package("aquamarine", CHECKSUM_B, "[hyprutils]"),
            ]
        )
        parsed = parse_manifest(manifest(packages))
        self.assertEqual(
            [["hyprutils"], ["aquamarine"], ["hyprland"]],
            parsed.build_waves(),
        )

    def test_independent_packages_share_a_sorted_wave(self) -> None:
        packages = "\n" + "\n".join(
            [package("zeta", CHECKSUM_A), package("alpha", CHECKSUM_B)]
        )
        parsed = parse_manifest(manifest(packages))
        self.assertEqual([["alpha", "zeta"]], parsed.build_waves())

    def test_unknown_dependency_is_rejected(self) -> None:
        packages = "\n" + package("hyprland", CHECKSUM_A, "[missing]")
        with self.assertRaisesRegex(ManifestError, "unknown packages: missing"):
            parse_manifest(manifest(packages))

    def test_dependency_cycle_is_rejected(self) -> None:
        packages = "\n" + "\n".join(
            [
                package("alpha", CHECKSUM_A, "[beta]"),
                package("beta", CHECKSUM_B, "[alpha]"),
            ]
        )
        with self.assertRaisesRegex(ManifestError, "contains a cycle"):
            parse_manifest(manifest(packages))

    def test_duplicate_yaml_key_is_rejected(self) -> None:
        duplicate = textwrap.dedent(
            """\
            schema: 1
            schema: 1
            release_set: "2026-09-01.1"
            packages: {}
            """
        )
        with self.assertRaisesRegex(ManifestError, "duplicate key 'schema'"):
            parse_manifest(duplicate)

    def test_bad_checksum_is_rejected(self) -> None:
        packages = "\n" + package("hyprutils", "not-a-checksum")
        with self.assertRaisesRegex(ManifestError, "64 lowercase hex digits"):
            parse_manifest(manifest(packages))

    def test_bad_source_commit_is_rejected(self) -> None:
        packages = "\n" + package("hyprutils", CHECKSUM_A)
        text = manifest(packages).replace(COMMIT_A, "unsigned-tag")
        with self.assertRaisesRegex(ManifestError, "40 lowercase hex digits"):
            parse_manifest(text)

    def test_placeholder_version_is_rejected(self) -> None:
        text = manifest("{}").replace(
            "packages: {}",
            textwrap.dedent(
                f"""\
                packages:
                  hyprutils:
                    upstream: https://github.com/hyprwm/hyprutils
                    version: TBD
                    source_commit: "{COMMIT_A}"
                    source_sha256: "{CHECKSUM_A}"
                    tier: core
                    depends_on: []
                """
            ).rstrip(),
        )
        with self.assertRaisesRegex(ManifestError, "RPM-compatible"):
            parse_manifest(text)

    def test_invalid_release_date_is_rejected(self) -> None:
        text = manifest("{}").replace("2026-09-01.1", "2026-02-30.1")
        with self.assertRaisesRegex(ManifestError, "valid date"):
            parse_manifest(text)

    def test_non_string_field_name_is_rejected(self) -> None:
        text = manifest("{}") + "42: surprise\n"
        with self.assertRaisesRegex(ManifestError, "field names must be strings"):
            parse_manifest(text)

    def test_upstream_credentials_are_rejected(self) -> None:
        packages = "\n" + package("hyprutils", CHECKSUM_A)
        text = manifest(packages).replace(
            "https://github.com", "https://token@github.com"
        )
        with self.assertRaisesRegex(ManifestError, "without credentials"):
            parse_manifest(text)

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(ManifestError, "unknown fields: surprise"):
            parse_manifest(manifest("{}") + "surprise: true\n")


class RepositoryCheckTests(unittest.TestCase):
    def _write_package(
        self,
        root: Path,
        *,
        checksum: str = CHECKSUM_A,
        build_line: str = "%meson",
        source0: str = "%{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz",
    ) -> None:
        build_lines = build_line.replace("\n", "\n                ")
        directory = root / "packages" / "hyprutils"
        directory.mkdir(parents=True)
        (directory / "sources").write_text(
            f"{checksum}  hyprutils-1.2.3.tar.gz\n", encoding="utf-8"
        )
        (directory / "hyprutils.spec").write_text(
            textwrap.dedent(
                f"""\
                Name: hyprutils
                Version: 1.2.3
                Release: 1%{{?dist}}
                Summary: Test
                License: BSD-3-Clause
                URL: https://github.com/hyprwm/hyprutils
                Source0: {source0}

                %description
                Test package.

                %build
                {build_lines}
                """
            ),
            encoding="utf-8",
        )

    def _parsed_manifest(self):
        packages = "\n" + package("hyprutils", CHECKSUM_A)
        return parse_manifest(manifest(packages))

    def test_package_files_match_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(root)
            check_repository(root, self._parsed_manifest())

    def test_source_checksum_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(root, checksum=CHECKSUM_B)
            with self.assertRaisesRegex(ManifestError, "does not match manifest"):
                check_repository(root, self._parsed_manifest())

    def test_network_command_in_build_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(root, build_line="curl https://example.invalid/source")
            with self.assertRaisesRegex(ManifestError, "network command in %build"):
                check_repository(root, self._parsed_manifest())

    def test_network_command_after_rpm_macro_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(
                root, build_line="%meson\n%meson_build\ncurl https://example.invalid/source"
            )
            with self.assertRaisesRegex(ManifestError, "network command in %build"):
                check_repository(root, self._parsed_manifest())

    def test_source_host_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(
                root,
                source0="https://example.invalid/hyprutils-1.2.3.tar.gz",
            )
            with self.assertRaisesRegex(ManifestError, "Source0 host"):
                check_repository(root, self._parsed_manifest())

    def test_privileged_scriptlet_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(root, build_line="%meson\n%post\necho unsafe")
            with self.assertRaisesRegex(ManifestError, "privileged RPM scriptlet"):
                check_repository(root, self._parsed_manifest())

    def test_unlisted_package_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_package(root)
            (root / "packages" / "surprise").mkdir()
            with self.assertRaisesRegex(ManifestError, "missing from package-set.yaml"):
                check_repository(root, self._parsed_manifest())


if __name__ == "__main__":
    unittest.main()
