# Repository instructions

This repository packages the Hyprland stack for COPR `dtutila/hyprland`.
`libsecret` belongs to `dtutila/utils`. Supported targets are Fedora 44 and 45,
x86_64; do not describe aarch64 as supported until built and tested.

## Update and validate

- Read `docs/operations.md`, `docs/build-and-test.md`, and
  `docs/security-audit.md` before changing or releasing packages.
- Update `package-set.yaml`, spec versions/releases, source checksums and patches
  together. Verify the upstream build system from the verified source archive.
- Keep plugin build/runtime dependencies pinned to the exact Hyprland RPM
  version-release; rebuild ABI consumers when their dependencies change.
- Run `./scripts/check` and `FEDORA=45 ./scripts/check-container`. Missing native
  RPM tools must trigger the Podman checks, never a silent success.
- Before COPR, build every package with `./scripts/build-container --fedora 44`
  and `--fedora 45`. Preserve results and investigate every failure.
- Use disposable Podman containers for installs/upgrades and runtime testing.
  Keep signatures enabled for COPR RPMs. Source builds run offline as a nonroot
  user, without host credentials, display, D-Bus or home mounts.
- Record exact builds, signatures, dependency/upgrade results, runtime coverage
  and limitations in `releases/<release-set>.json` and the validation document.
  Build success and `--version` do not establish desktop or plugin correctness.

## Submit and publish

- Use a release-set branch and immutable Git commit for COPR submissions. The
  repo-local SSH identity is `~/.ssh/id_ed25519_dtutila`; do not change the global
  GitHub identity or print credentials.
- Keep COPR manual publication enabled (`devel_mode=true`) and build networking
  disabled. Builds do not become public until repository metadata is regenerated.
- Download the exact signed candidate build artifacts and test those RPMs on
  both targets. Inspect other pending builds because regeneration is project-wide.
- When the user authorizes publication and the required checks pass, run
  `copr-cli regenerate-repos dtutila/hyprland`; do not ask again for authorization
  already given. If a required test fails or is unavailable, report the concrete
  limitation rather than recording a pass or silently bypassing the gate.
- Verify the expected versions through fresh public metadata and signed installs
  on both targets. Record publication time and evidence, then fast-forward the
  tested release into `main` and push. Keep manual mode enabled for future work.
- Document reusable procedures in the repository, not only session memory.
  Remove only temporary containers/images created by this task; never prune
  unrelated Podman objects or interrupt the user's desktop session.
