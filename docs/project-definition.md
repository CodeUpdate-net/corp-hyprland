# Project definition

## Summary

Build and maintain a small Fedora COPR named `<FAS_USERNAME>/hyprland` that
delivers a current, internally compatible Hyprland stack for supported Fedora
releases. It is an overlay, not a general desktop repository: it contains
Hyprland, first-party `hyprwm` applications, and only those library or toolchain
dependencies needed to build and run them.

The project takes inspiration from
[`lionheartp/Hyprland`](https://copr.fedorainfracloud.org/coprs/lionheartp/Hyprland/)
but removes Noctalia, shells, bars, terminals, wallpaper front ends, and other
unrelated desktop customizations.

## Problem

Fedora carries Hyprland and several related libraries, but Fedora's update
cadence can trail upstream. Hyprland's libraries and plugins also evolve
together, so mixing a newer compositor with older system libraries can produce
unresolved dependencies, symbol lookup failures, or plugin ABI failures.

Users need one repository whose releases are tested and published as a
coherent set, without turning that repository into a full opinionated desktop
distribution.

## Goals

- Publish stable upstream Hyprland releases promptly for supported Fedora
  versions.
- Treat the ABI-coupled Hyprland libraries, compositor, and plugins as one
  release set.
- Provide first-party utilities that make a practical Hyprland session.
- Build for `x86_64` and `aarch64` from the same source definitions.
- Use reproducible source RPMs, isolated Mock/COPR builds, and auditable source
  provenance.
- Reuse Fedora packages whenever they satisfy the required version and ABI.
- Document releases and recovery well enough for a single maintainer to
  operate the project safely.

## Non-goals

- Shipping Noctalia or its dependencies.
- Curating a complete desktop, dotfiles, themes, fonts, terminals, bars,
  launchers outside `hyprwm`, or a Fedora spin.
- Replacing Fedora dependencies merely to make them newer.
- Supporting EPEL, immutable-image composition, or architectures that are not
  tested in the first release.
- Publishing nightly/git snapshots in the production project.
- Becoming the upstream Fedora package source during the MVP. Improvements can
  be proposed to Fedora later.

## Users

- Fedora users who want a newer stable Hyprland stack than their Fedora release
  currently supplies.
- The maintainer, who needs a predictable update and rollback workflow.
- Contributors adding a Hyprland-owned utility or fixing a Fedora-specific
  build issue.

## Product policy

1. **Stable first.** Package signed upstream tags. A separate COPR may be
   proposed later for snapshots.
2. **One coherent stack.** Build libraries before consumers, Hyprland after its
   libraries, and plugins after the exact Hyprland build they target.
3. **Small overlay.** A package is admitted only when it passes the inclusion
   test in [package-scope.md](package-scope.md).
4. **Fedora first.** Specifications follow Fedora packaging conventions and
   use system libraries unless a documented compatibility exception is needed.
5. **Atomic publication.** Builds remain in COPR's development repository
   until the complete release set passes its gates; then repository metadata is
   regenerated once.
6. **No silent breakage.** A failed target chroot blocks publication unless it
   is explicitly removed from the supported matrix with a documented reason.

## Success criteria

The MVP is successful when:

- every required package builds on all declared chroots and both architectures;
- `dnf` can install and upgrade the stack in a clean Fedora test root without
  dependency conflicts;
- the installed compositor and utilities report the expected versions;
- the matching plugin package loads against the published Hyprland build;
- repository closure passes;
- a fresh user can enable the COPR and install `hyprland` using the documented
  commands;
- an update and a rollback have each been rehearsed once.

## Constraints and risks

| Risk | Project response |
| --- | --- |
| Hyprland library/plugin ABI changes | Rebuild and promote the whole affected release set together. |
| Fedora already has an older package with the same name | Publish only when the COPR EVR is intentionally newer; test upgrade and downgrade paths. |
| Rawhide changes underneath the build | Treat Rawhide as an early-warning target, not evidence that stable Fedora works. |
| Upstream requires a dependency Fedora lacks or versions incompatibly | Add a narrowly scoped compatibility package, document why, and remove it when Fedora catches up. |
| A build succeeds but the repository is temporarily inconsistent | Use manual repository publication (`devel_mode`) and promote only a complete set. |
| Reference packaging has unclear reuse rights | Do not copy it until its license/provenance is confirmed; implement from upstream and Fedora references in the meantime. |
| Maintainer credentials leak into Git | Store COPR and forge tokens only in local config or CI secret storage. |

## Initial decisions

- **Repository strategy:** start clean rather than immediately forking
  `LionHeartP/hyprlandRPM`. Its public tree had no repository-level `LICENSE`
  file at the 2026-09-01 review. A GitHub fork is technically possible, but
  reuse and redistribution beyond GitHub's fork mechanism should be confirmed
  with the author first.
- **Build source:** one packaging monorepo, one directory per source package,
  exposed to COPR as SCM packages using the `make_srpm` source-build method.
  The source stage downloads and verifies upstream archives; binary builds
  remain network-disabled.
- **Release channel:** stable tags only.
- **Architectures:** `x86_64` and `aarch64`.
- **Publication:** manual/atomic repository generation after release-set tests.
- **Project license:** unresolved. Select a license before publishing the
  repository or accepting external contributions; do not import third-party
  implementation files before then, and record per-file provenance separately.

## Open owner choices

These do not block package prototyping, but must be resolved before creating
the production COPR:

- the FAS username or COPR group that owns the project;
- the public Git repository URL;
- the repository's license;
- whether Fedora Branched is a required target or best-effort target;
- the support/contact URL displayed by COPR.
