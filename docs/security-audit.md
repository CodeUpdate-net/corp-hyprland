# Security audit and release gate

## Audit procedure

Run this for every release, recording exact source revisions and results:

1. Review the manifest/spec/patch diff. Independently verify upstream tag or
   commit provenance, HTTPS source location, SHA-256, licenses and patch origin.
   A checksum detects changed bytes; it does not authenticate the upstream author.
2. Run `./scripts/check` on both Fedora targets. It rejects source mismatches,
   missing upstream build-system files, unlisted package dependencies, loose
   plugin ABI pins, explicit privileged scriptlets and known build-stage network
   commands. Static scanning is a guardrail, not a shell interpreter or sandbox.
3. Build all packages with `scripts/build-container` on both targets. Source
   compilation is offline and unprivileged. Run a clean Mock build before release.
4. Inspect the resulting RPMs with `rpm -qp --scripts`, `--requires`, `--provides`,
   and `-qplv`; inspect setuid/capability-bearing files, system/user services,
   world-writable paths, bundled libraries and unexpected executable content.
   RPM macros can generate scriptlets even when no explicit scriptlet is in the
   spec, so inspect the actual RPM as well.
5. Review security-sensitive changes: shell command arguments, temporary files,
   archive paths, IPC, polkit/PAM prompts, lock/unlock and plugin loading. Test
   malformed inputs in disposable containers or VMs, never against personal data.
6. Check upstream security advisories for each pinned version and record the
   search date, sources and applicable fixes. No repository check establishes
   that all upstream code is free of vulnerabilities.
7. Run install/upgrade and VM session gates in [operations.md](operations.md).
   Keep signature verification on for COPR artifacts. Freeze the candidate before
   testing; publish only the exact reviewed builds.

On a security incident, freeze publication, preserve evidence and privately
coordinate with the project owner/upstream. Prepare a patched candidate, rebuild
ABI-sensitive consumers, repeat the gates and record a recovery release.

## Findings from the 2026-09-18 packaging review

- `scripts/check` returned success when RPM tooling was absent. It now uses a
  Fedora Podman fallback and fails if required checks cannot run. Partial checking
  requires the explicit `--metadata-only` option.
- The old scratch build loop could report completion after failed packages or
  linting. The tracked build script stops on failures, records exact coverage,
  and builds without network access in a separate unprivileged container.
- hyprland-protocols 0.7.1 contains CMakeLists.txt and no root meson.build. The
  existing CMake correction is consistent with its pinned source. A regression
  test ensures that the old Meson spec would fail source validation.
- hyprland-plugins had a broad `>= 0.56.0` dependency despite consuming internal
  compositor headers. Both build and runtime dependencies now pin
  `hyprland = 0.56.2-4` for the target Fedora distribution. Future compositor
  releases must rebuild and update this pin. See the
  [upstream plugin version guidance](https://wiki.hypr.land/Plugins/Using-Plugins/).
- hyprcursor-util used shared `/tmp/hyprcursor-util` storage while converting
  cursors. The additional downstream patch uses `mkdtemp` private directories,
  one per cursor, with cleanup when its scope exits. This removes
  shared-directory symlink/concurrency risks while retaining the existing shell
  quoting patch. The patch changes the utility, not the library ABI.
- Static checks now include transaction/file trigger scriptlets and network
  commands in `%generate_buildrequires`, and check source filenames more strictly.
- `docs/` was ignored rather than tracked. Operational and security procedures
  are now included in repository changes, rather than depending on local memory.

## Reviewed rpmlint exceptions

`scripts/rpmlint.toml` contains narrow filters, not a permissive global exit:

- Hyprland/wlroots spelling diagnostics are proper project names.
- The named Hyprland plugin and Qt style/engine `.so` objects intentionally use
  unversioned module names. The compositor plugin relationship is explicitly
  pinned; review these paths again if upstream changes its installation layout.
- UWSM's named plugins are mode-0644 sourced shell fragments with `/bin/false`
  shebangs to prevent direct execution. Making them executable to silence lint
  would misrepresent their interface.

Missing man pages, missing devel-package documentation and packages without
upstream `%check` suites remain visible warnings. They are not evidence of
runtime safety. Review any new error rather than broadening these filters.

## Evidence and limits

See [validation-2026-09-18.md](validation-2026-09-18.md) for observed checks and
outstanding release gates. Audit fixes in this working tree require new builds
and deliberate publication before users receive them.
