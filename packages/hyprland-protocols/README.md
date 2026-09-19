# hyprland-protocols packaging notes

## Selected source

- Upstream: <https://github.com/hyprwm/hyprland-protocols>
- Version/tag: `0.7.1` / `v0.7.1`
- Commit: `cc9a8fd253bdc00f48a967ecf4828211ef08751f`
- Source archive: `https://github.com/hyprwm/hyprland-protocols/archive/refs/tags/v0.7.1.tar.gz`
- SHA-256: `178fa406a1c76e94efeed5d1488abd6029427865f6fd4caf296c71ffaf0d069e`
- Upstream license: BSD-3-Clause

The selected Hyprland stack requires protocol metadata >= 0.7.0. The source
archive and its hash were checked against `package-set.yaml` on 2026-09-18.

## Provenance

The original spec was written for this project using upstream v0.7.0 build
and installation definitions and Fedora packaging guidelines. No spec was
copied from the LionHeartP or solopasha repositories. Package naming and the
`-devel` split match Fedora's interface.

Upstream 0.7.1 removed the root Meson build and switched to CMake. The spec was
corrected accordingly; `scripts/source_check.py` now catches a spec still using
Meson against this archive.

## Build and validation

This is a noarch, development-only package. CMake installs XML files beneath
`%{_datadir}/hyprland-protocols/protocols` and pkg-config metadata beneath
`%{_datadir}/pkgconfig`. Upstream provides no test suite for this release; there
is no `%check` section pretending to run one.

```bash
./scripts/check
./scripts/build-container --fedora 44 --package hyprland-protocols
```

Run from the repository root. Repeat on Fedora 45 and build the full package
set before COPR submission. See [the Podman guide](../../docs/build-and-test.md).
