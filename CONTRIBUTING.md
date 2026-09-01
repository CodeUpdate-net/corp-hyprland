# Contributing

The project is in its bootstrap phase. Discuss substantial packaging changes
before investing in a complete spec, because every additional overlay package
increases the supported ABI and upgrade surface.

## Package changes

Every package change must:

- satisfy the inclusion test in [`docs/package-scope.md`](docs/package-scope.md);
- use an immutable HTTPS source with a SHA-256 checksum;
- record the origin and license of specs, patches, and other imported files;
- avoid network access during RPM build stages;
- declare direct in-repository build dependencies in `package-set.yaml`; and
- pass `./scripts/check`.

Add new packages under `packages/<source-package>/`. A package directory will
eventually contain its spec, source metadata, package notes, and any patches.
Do not commit source archives, RPMs, build roots, build logs, or credentials.

## Provenance

Until the repository license is selected, contribute only original work that
you have permission to submit. Do not copy files from the unlicensed reference
packaging repository. For imported Fedora packaging, preserve applicable
copyright and license notices and identify the dist-git commit and file origin
in the package README.
