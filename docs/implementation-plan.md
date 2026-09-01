# Implementation plan

## Phase 0 — resolve ownership and reuse

Deliverables:

- record the FAS/COPR owner, Git forge URL, contact URL, and repository license;
- ask the `LionHeartP/hyprlandRPM` maintainer to clarify the packaging
  repository's reuse license if any files will be ported;
- create a per-file provenance rule for imported specs and patches;
- if a fork is approved, apply the allowlist in
  [package-scope.md](package-scope.md) and remove stale package definitions from
  COPR as well as Git;
- verify active COPR chroots and Fedora support status.

Exit gate: the repository can accept code without unresolved ownership or
license ambiguity.

## Phase 1 — repository skeleton and validation

Deliverables:

- create the layout in [architecture.md](architecture.md);
- define and validate `package-set.yaml`;
- add `.gitignore`, contribution guidance, a security policy, and license;
- implement scripts that derive a dependency order and verify sources/specs;
- add CI for formatting, schema checks, spec parsing, source checksums, and
  `rpmlint`.

Exit gate: a deliberately minimal example package can produce an SRPM locally
and CI fails for a bad checksum or dependency cycle.

## Phase 2 — core package prototypes

Start from current Fedora dist-git where suitable, then update it to the chosen
upstream tags. Preserve changelog/provenance when importing work. Package in
dependency order:

1. protocols, scanner, `hyprutils`;
2. `hyprlang`, `hyprgraphics`, `hyprcursor`, `hyprwire`;
3. `aquamarine`, `hyprtoolkit`, and required Qt support;
4. `hyprland`;
5. `hyprland-plugins`.

For every package:

- document why Fedora's package cannot be used directly on each target;
- pin and checksum sources;
- eliminate build-time network access;
- run `%check` where upstream supplies tests;
- review generated Requires/Provides and library ABI metadata;
- perform a clean Mock build.

Exit gate: Hyprland and matching plugins install from a local repository on a
clean Fedora VM and pass a nested/VM smoke session.

## Phase 3 — first-party applications

Add applications from [package-scope.md](package-scope.md) in dependency order.
Do not block the core release for an optional application unless it is required
for a minimally functional session.

Exit gate: all applications selected for MVP build and install across the
required matrix; desktop, D-Bus, systemd user, PAM, and portal integration files
are reviewed for Fedora paths and permissions.

## Phase 4 — COPR staging

Deliverables:

- create the production COPR from [copr-project.md](copr-project.md);
- add SCM package definitions with production auto-rebuild disabled;
- submit dependency-ordered batches into the development repository;
- capture COPR build IDs in a release manifest;
- run repoclosure, clean install, upgrade, command smoke, plugin, and VM session
  tests.

Exit gate: every required chroot is green and no package is visible publicly
until the complete release set is ready.

## Phase 5 — first publication

Deliverables:

- regenerate COPR repository metadata once;
- test the exact public install commands on clean Fedora systems;
- publish supported Fedora releases/architectures and known limitations;
- publish the release manifest and rollback target;
- enable a build-status badge only after it represents the supported matrix.

Exit gate: the success criteria in [project-definition.md](project-definition.md)
are met and the runbook has been rehearsed.

## Phase 6 — update automation

Automate only after one manual release has succeeded:

- detect stable upstream tags and open version-update pull requests;
- refresh archives/checksums and changelog stubs;
- build PRs in isolated COPR subprojects without production secrets;
- require maintainer approval for production builds and publication;
- add Fedora branching/EOL reminders and dependency-overlay retirement checks.

## MVP definition of done

- [ ] Ownership, license, and provenance policy are resolved.
- [ ] Package manifest and dependency graph validate in CI.
- [ ] All core specs build locally in clean Mock roots.
- [ ] All required COPR chroots succeed on `x86_64` and `aarch64`.
- [ ] Noctalia and unrelated desktop packages are absent.
- [ ] Repository closure and clean transaction tests pass.
- [ ] Hyprland session and plugin compatibility smoke tests pass.
- [ ] Public installation and removal paths are verified.
- [ ] Release and rollback procedures are rehearsed.
- [ ] The first release manifest is committed.
