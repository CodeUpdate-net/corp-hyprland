# Hyprland COPR documentation

Current operating instructions:

1. [Build and test with Podman](build-and-test.md)
2. [Build, publish and rollback runbook](operations.md)
3. [Observed COPR settings and target matrix](copr-project.md)
4. [Security audit procedure and findings](security-audit.md)
5. [2026-09-18 validation record](validation-2026-09-18.md)

The project is `dtutila/hyprland`, sourced from
`https://github.com/CodeUpdate-net/corp-hyprland.git`, with Fedora 44/45 x86_64
chroots. aarch64 is deferred. libsecret belongs separately in `dtutila/utils`.
Publication is manual and binary-build networking is disabled.

Design background, originally written during bootstrap:

- [Project definition](project-definition.md)
- [Package scope](package-scope.md)
- [Repository architecture](architecture.md)
- [Implementation plan](implementation-plan.md)
- [Research references](references.md)

Those design documents contain proposed future capabilities and historical
snapshots. The current runbook and observed project settings take precedence
over bootstrap examples. Neither design intent nor an available COPR chroot is
proof of a tested release or supported architecture.
