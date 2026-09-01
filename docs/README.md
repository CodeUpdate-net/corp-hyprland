# Hyprland COPR documentation

This directory is the implementation handoff for a focused Fedora COPR that
ships current Hyprland releases, first-party Hyprland applications, and the
minimum dependency overlay needed to keep that stack ABI-compatible.

Start here:

1. [Project definition](project-definition.md) — purpose, scope, success
   criteria, and decisions.
2. [Package scope](package-scope.md) — the initial package inventory and the
   rules for adding or removing packages.
3. [Repository and build design](architecture.md) — proposed repository
   layout, source flow, dependency ordering, and CI design.
4. [COPR project definition](copr-project.md) — intended COPR settings and
   bootstrap commands.
5. [Implementation plan](implementation-plan.md) — sequenced work, acceptance
   gates, and the definition of done.
6. [Operations runbook](operations.md) — update, release, rollback, and Fedora
   branching procedures.
7. [Research and references](references.md) — sources consulted and the
   time-sensitive facts that must be rechecked.

## Working assumptions

- “corp” in the original request means Fedora **COPR**.
- The proposed COPR name is `hyprland`; replace `<FAS_USERNAME>` everywhere
  with the account or COPR group that will own it.
- The production channel follows stable upstream tags. Snapshot (`-git`)
  packages are deliberately outside the first release.
- Noctalia is intentionally excluded. Fedora-provided packages are reused
  unless a newer or coherently rebuilt package is required by Hyprland.
- The first supported architectures are `x86_64` and `aarch64`.

These assumptions let implementation start without binding the repository to
a personal account name or a Git forge that has not yet been selected.
