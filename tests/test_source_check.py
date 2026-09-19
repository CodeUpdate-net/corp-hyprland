from __future__ import annotations
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from package_set import ManifestError
from source_check import check_archive


class SourceCheckTests(unittest.TestCase):
    def archive(self, directory, names):
        path = Path(directory) / 'source.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name in names:
                member = tarfile.TarInfo(name)
                member.size = 4
                archive.addfile(member, io.BytesIO(b'test'))
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_cmake_port_rejects_stale_meson_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            path, digest = self.archive(directory, ['pkg/CMakeLists.txt'])
            with self.assertRaisesRegex(ManifestError, 'spec build system'):
                check_archive(path, digest, '%build\n%meson\n%install\n')
            check_archive(path, digest, '%build\n%cmake\n%install\n')

    def test_nested_cmake_does_not_mask_missing_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path, digest = self.archive(directory, ['pkg/vendor/CMakeLists.txt'])
            with self.assertRaisesRegex(ManifestError, 'source root'):
                check_archive(path, digest, '%build\n%cmake\n')

    def test_checksum_checked_before_archive_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = self.archive(directory, ['pkg/CMakeLists.txt'])
            with self.assertRaisesRegex(ManifestError, 'SHA-256 mismatch'):
                check_archive(path, '0' * 64, '%build\n%cmake\n')

    def test_path_traversal_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path, digest = self.archive(directory, ['pkg/../../escape'])
            with self.assertRaisesRegex(ManifestError, 'unsafe archive path'):
                check_archive(path, digest, '%build\n%cmake\n')

    def test_changelog_does_not_select_build_system(self):
        with tempfile.TemporaryDirectory() as directory:
            path, digest = self.archive(directory, ['pkg/meson.build'])
            check_archive(path, digest, '%build\n%meson\n%install\n%changelog\n%cmake\n')

class RepositoryRegressionTests(unittest.TestCase):
    def test_security_scriptlet_variants_rejected(self):
        from repository_check import _check_no_scriptlets
        for scriptlet in ['pretrans', 'posttrans', 'filetriggerin', 'transfiletriggerun', 'verifyscript']:
            with self.subTest(scriptlet=scriptlet), self.assertRaisesRegex(ManifestError, 'privileged'):
                _check_no_scriptlets(Path('test.spec'), f'%{scriptlet}\necho unsafe\n')

    def test_dynamic_buildrequires_network_rejected(self):
        from repository_check import _check_no_build_network
        with self.assertRaisesRegex(ManifestError, 'network command'):
            _check_no_build_network(Path('test.spec'), '%generate_buildrequires\ncurl https://example.test/source\n')

    def test_source_filename_rejects_dotdot_and_options(self):
        from repository_check import _source_filename
        for name in ['..', '-output', 'bad name']:
            with self.subTest(name=name), self.assertRaises(ManifestError):
                _source_filename(f'https://example.test/archive#/{name}', Path('test.spec'))

    def test_plugin_pin_and_dependency_graph_regressions(self):
        from repository_check import check_repository
        from package_set import load_manifest
        import shutil
        source = Path(__file__).resolve().parents[1]
        manifest = load_manifest(source / 'package-set.yaml')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for package in manifest.packages:
                target = root / 'packages' / package
                target.mkdir(parents=True)
                for path in (source / 'packages' / package).iterdir():
                    if path.is_file() and not path.name.endswith('.tar.gz'):
                        shutil.copy(path, target)
            check_repository(root, manifest)
            spec = root / 'packages/hyprland-plugins/hyprland-plugins.spec'
            original = spec.read_text()
            spec.write_text(original.replace('hyprland%{?_isa} =', 'hyprland%{?_isa} >='))
            with self.assertRaisesRegex(ManifestError, 'must pin'):
                check_repository(root, manifest)
            spec.write_text(original)
            from dataclasses import replace
            packages = dict(manifest.packages)
            packages['hyprland-plugins'] = replace(packages['hyprland-plugins'], depends_on=())
            with self.assertRaisesRegex(ManifestError, 'missing from depends_on'):
                check_repository(root, replace(manifest, packages=packages))
