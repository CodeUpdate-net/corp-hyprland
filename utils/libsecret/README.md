# libsecret for dtutila/utils

COPR target: **dtutila/utils**, Fedora 44/45 x86_64. This recipe is maintained
outside the Hyprland `packages/` directory and `package-set.yaml`.

Version 0.21.8.2 uses the official GNOME archive and Fedora's GnuTLS configuration,
license declaration and runtime/devel/mock-service subpackages. Release 2.1
sorts after Fedora 44's 0.21.8.2-2 while allowing later Fedora release 3 to win.
There are no downstream source patches. Installed non-executable mock-service
helpers have their obsolete executable shebangs removed. `rpmlint.toml` limits
exceptions to the gnome-keyring name and unchanged upstream license postal
addresses. `%check` requires a private D-Bus test
setup and runs all 25 upstream tests, including Python, JavaScript and Vala.
The PAM module and TPM2 support remain disabled as in the original Fedora recipe.

Verify `sources`, install the spec's BuildRequires in a disposable Fedora
container, and run `rpmbuild -ba` offline as an unprivileged user on both targets.
Test upgrades from the prior public COPR build, `dnf check`, and installed
`secret-tool` store/lookup/clear operations using a private D-Bus mock service.
Do not use the user's actual keyring or session bus for package tests.

Submit with an immutable release-branch commit:

```bash
copr-cli buildscm dtutila/utils \
  --clone-url https://github.com/CodeUpdate-net/corp-hyprland.git \
  --commit COMMIT --subdir utils/libsecret --spec libsecret.spec \
  --type git --method make_srpm --enable-net off --nowait
```

Keep manual publication enabled. Download and verify the exact signed builds,
repeat installation/runtime checks, inspect other pending builds, then run
`copr-cli regenerate-repos dtutila/utils` when publication is authorized. Verify
fresh public metadata and signed installs afterward. Record the evidence under
`releases/utils-libsecret-<version>.json`.

## Future automatic builds

A scheduled CI workflow can check GNOME's stable release index, open a release
branch with the spec/checksum change, run both Fedora container builds and
upstream/runtime/upgrade tests, then submit the passing immutable commit to
COPR. Keep COPR credentials in protected CI secrets, never in repository files
or workflows triggered by untrusted pull requests. Serialize submissions per
package to prevent overlapping candidates.

Automatic building and publication are separate: keep `devel_mode=true` so
successful candidates await deliberate repository regeneration. A fully
unattended publisher would also need to download signed artifacts, run the
post-build tests, inspect project-wide pending builds and verify public results.

No scheduled updater is installed by this package update. COPR's previous
package source followed Fedora's `f44` DistGit branch with `auto_rebuild=false`;
that alone did not monitor GNOME releases. The immutable SCM submission above
provides the recipe for this update.
