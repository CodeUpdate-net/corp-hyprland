# Build and test with Podman

Run these commands from the checkout root. The supported validation matrix is
Fedora 44 and 45 on x86_64. aarch64 has not been enabled or validated.

## Prerequisites and fast checks

On Fedora, install Podman, Python and PyYAML:

```bash
sudo dnf install podman python3-pyyaml
./scripts/check --metadata-only
./scripts/check
FEDORA=45 ./scripts/check-container
./scripts/render-build-order
```

`check --metadata-only` is explicitly a partial check. The normal `check` requires
RPM parsing, RPM lint and verified source/build-system checks. If native RPM
tools are absent, it invokes `check-container`, which builds the dedicated
`localhost/corp-validation:f44` image from `scripts/Containerfile`. It fails if
Podman cannot run. No RPM checks are silently skipped.

The container installs Fedora's CMake, Meson and systemd macros, copies the
read-only checkout into its own filesystem, and downloads any missing archives.
`source_check.py` verifies SHA-256 before reading archive members and checks that
the spec's chosen build system exists at the upstream source root. This catches
the hyprland-protocols 0.7.1 Meson-to-CMake change. It does not prove that all
configure options or dependencies are correct; binary builds remain required.

To check cached sources without downloading, or populate the local cache:

```bash
python3 scripts/source_check.py
python3 scripts/source_check.py --download
```

## Build every package before COPR

```bash
./scripts/build-container --fedora 44
./scripts/build-container --fedora 45
```

For a targeted development build, including its manifest dependencies:

```bash
./scripts/build-container --fedora 44 --package hyprcursor
```

Each run creates `results/fedora-<release>-<timestamp>/`, containing a frozen
input copy, `result.json`, per-package logs, `rpms/`, `srpms/`, `install.log` and
`rpmlint.log`. A nonzero exit or any status other than `passed` blocks release.
Targeted runs are not a substitute for the full 29-package gate.

The script derives order from `package-set.yaml`. For each package it starts a
fresh container, exposes only Fedora and the RPMs already built in this run,
installs that spec's BuildRequires, then commits a temporary prepared image.
It builds the SRPM and binary RPMs as `builder` with `--network=none`, without
host mounts in the build container. `%prep`, `%build`, `%install` and `%check`
therefore cannot download dependencies. The final gate installs all produced
packages in a separate disposable container, runs `dnf check`, and lints the
binaries. Documented lint exceptions are in `scripts/rpmlint.toml`.

The unsigned repository of locally built RPMs is trusted only inside the
throwaway build containers. Public COPR installs keep package signature checking
enabled. Do not mount your home, SSH agent, credentials, display, D-Bus socket,
or container socket into source-build containers. No privileged Podman mode is
needed. The scripts create and remove only their own temporary objects; they
do not prune other images or pods. SELinux `:z` sharing is limited to the checkout
and results directories.

This is a package build/install gate, not a desktop-session test. Before
publication, also run a clean Mock build for each target, an upgrade from Fedora
packages, and the VM session checks in [operations.md](operations.md). A container
cannot validate GPU access, screen locking, PAM prompts or a real portal session.

## Desktop and plugin runtime tests

Follow [runtime-testing.md](runtime-testing.md) to run the signed candidates in
a nested compositor inside disposable Podman containers. Record actual coverage
and remaining hardware/session limitations.

## Native SRPM and Mock alternatives

```bash
sudo dnf install rpm-build rpmdevtools python3-pyyaml mock
./scripts/build-local hyprland-protocols
mock -r fedora-44-x86_64 --rebuild results/srpm/hyprland-protocols/*.src.rpm
```

`build-local` produces only an SRPM. It is not a binary or runtime test. For
packages with overlay dependencies, configure Mock with a local repository of
the already-built dependency waves and keep binary-build networking disabled.
Do not satisfy an isolated-build test from the public COPR: that can hide a
missing dependency edge or an old ABI.

Podman options: [official run documentation](https://docs.podman.io/en/stable/markdown/podman-run.1.html).

## Retry a interrupted build

For runs created by the current script, `--resume` checks the frozen manifest,
all package inputs, the Fedora image ID and all completed RPM checksums before
reusing any completed packages:

```bash
./scripts/build-container --fedora 44 --resume results/fedora-44-<timestamp>
```

Use the same `--package` selection if the original run was targeted. Changed
inputs, extra/modified RPMs, a changed image or older results without artifact
checksums require a new run. Do not resume a directory while another build is
using it. Use `--jobs 2` on memory-constrained machines (default: 4).
