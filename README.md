# Hyprland COPR

Packaging source for [dtutila/hyprland](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/):
stable Hyprland, first-party applications and the dependency overlay needed to
keep them compatible. Current targets are Fedora 44 and 45 on x86_64. aarch64 is
not yet enabled. libsecret belongs separately in `dtutila/utils`.

## Build and test

```bash
sudo dnf install podman python3-pyyaml
./scripts/check
./scripts/build-container --fedora 44
./scripts/build-container --fedora 45
```

`check` uses Fedora in Podman when host RPM tools are missing. Full container
builds verify every package in dependency order, compile without networking,
and preserve RPMs and logs under `results/`. Python 3.11+ and PyYAML 6 are required.

- [Podman build and test instructions](docs/build-and-test.md)
- [Nested desktop and plugin runtime tests](docs/runtime-testing.md)
- [Build, publish and rollback runbook](docs/operations.md)
- [Current COPR configuration](docs/copr-project.md)
- [Security audit procedure and findings](docs/security-audit.md)
- [Security patches, regression tests and limitations](docs/security-patches.md)

`package-set.yaml` pins versions, source checksums and dependency ordering.
Manual COPR publication is enabled: successful future builds remain candidates
until the operator intentionally regenerates repository metadata after testing.

The repository-wide license and private security contact still need an owner
decision. Preserve all third-party license/provenance notices.
