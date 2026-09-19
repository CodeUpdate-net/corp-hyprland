# COPR project configuration

Verified through the public API on 2026-09-18:

| Setting | Observed value |
| --- | --- |
| Project | `dtutila/hyprland` |
| Source | `https://github.com/CodeUpdate-net/corp-hyprland.git` |
| Chroots | `fedora-44-x86_64`, `fedora-45-x86_64` |
| Manual publication (`devel_mode`) | `true` |
| Binary-build networking (`enable_net`) | `false` |
| Follow Fedora branching | `true` |
| Automatic pruning | `true` |
| Storage | `pulp` |
| AppStream / module hotfixes | `false` / `false` |

Only x86_64 is configured. aarch64 is a future expansion requiring clean builds,
install/upgrade tests and runtime evidence; it is not currently supported.
Fedora 43 and Rawhide are not enabled in this project. Do not infer support from
a chroot's availability in another COPR. Review the matrix when Fedora branches.

The API still reports a personal-project description, `instructions: tbd`, and
no homepage/contact. Fill those in with reviewed user-facing installation and
support information when publishing the next release; they are not build gates.

```bash
curl -fsSL 'https://copr.fedorainfracloud.org/api_3/project?ownername=dtutila&projectname=hyprland' | python3 -m json.tool
copr-cli whoami
copr-cli modify --help
copr-cli list-chroots
```

The installed client uses the following spelling (verify `--help` when upgrading):

```bash
copr-cli modify dtutila/hyprland --disable_createrepo true --enable-net off
```

`devel_mode` holds new results out of public metadata until repository
regeneration. It does not roll back packages already published or freeze the
candidate repository while more builds run. Freeze submissions before testing
and promotion. See [operations.md](operations.md) for build and publication
commands and [COPR's manual-publication documentation](https://docs.pagure.org/copr.copr/user_documentation.html#manual-repository-management).

Keep credentials in `~/.config/copr` with mode 0600, outside this checkout and
outside build containers. Public API reads do not require credentials.

SCM builds use `make_srpm`, with `packages/<name>` as the subdirectory and
`<name>.spec` as the spec. `.copr/Makefile` downloads and checks Source0 in the
source-build stage. Binary builds must retain `enable_net=false`. Submit immutable
Git commit IDs and keep automatic production rebuilds disabled.

## Separate utility repository

**libsecret belongs in `dtutila/utils`, not `dtutila/hyprland`.** Keep its packaging,
builds, tests and publication in that project. This checkout does not contain a
libsecret package and does not enable `dtutila/utils` as an implicit dependency.
If a future Hyprland package needs it, first check whether Fedora's libsecret
satisfies the requirement; review any cross-project repository dependency explicitly.
