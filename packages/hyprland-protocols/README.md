# hyprland-protocols packaging notes

## Selection

- Upstream: <https://github.com/hyprwm/hyprland-protocols>
- Version/tag: `0.7.0` / `v0.7.0`
- Source archive: `https://github.com/hyprwm/hyprland-protocols/archive/refs/tags/v0.7.0.tar.gz`
- SHA-256: `ee419006d7cd20927b9b7c8b5fc430571c151b0385d600508de1a7957294498c`
- Upstream license: BSD-3-Clause

Hyprland requires `pkgconfig(hyprland-protocols) >= 0.7.0` in the selected
release line. At the 2026-09-01 review, Fedora 43, 44, and 45 provided 0.4.0,
so the official package cannot satisfy that build dependency.

## Provenance

The spec was written for this project from the v0.7.0 upstream Meson build and
install definitions plus Fedora's published packaging guidelines. No file was
copied from the LionHeartP or solopasha packaging repositories. Package naming
and the `-devel` split intentionally match Fedora so upgrades replace the same
interface cleanly.

The release archive was downloaded from the upstream tag URL and independently
hashed on 2026-09-01. The `sources` entry is in `sha256sum --check` format and
must match `package-set.yaml`.

## Build notes

This is a noarch, development-only package. Meson installs protocol XML files
under `%{_datadir}/hyprland-protocols` and pkg-config metadata under
`%{_datadir}/pkgconfig`. `%check` invokes Meson's test runner; upstream defines
no test cases for this release, so this currently verifies the configured test
project only.
