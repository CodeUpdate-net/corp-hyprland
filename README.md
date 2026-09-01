# Hyprland COPR

This repository is the packaging source for a focused Fedora COPR containing
stable Hyprland releases, first-party Hyprland applications, and only the
dependency overlay required to keep that stack compatible.

Implementation is in its bootstrap phase. No public COPR or installable
package set is available yet. The design and operating policy live in
[`docs/README.md`](docs/README.md).

## Developer quick start

The validation tools require Python 3.11 or newer and PyYAML 6.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
./scripts/check
./scripts/render-build-order
```

`package-set.yaml` is the source of truth for package versions and dependency
ordering. Packages are added only after their upstream tag, source checksum,
Fedora overlap, and provenance have been reviewed. The first prototype is
`hyprland-protocols`.

## Project status

The COPR owner, public forge URL, contact address, and repository license still
need owner decisions. Do not import third-party specs or patches until their
reuse terms and per-file provenance are recorded.
