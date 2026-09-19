# Research and references

Research snapshot: **2026-09-01**. Package versions, Fedora support windows,
COPR chroots, and CLI options are time-sensitive and must be checked again when
implementation starts.

## Reference projects and current state

- [lionheartp/Hyprland COPR](https://copr.fedorainfracloud.org/coprs/lionheartp/Hyprland/)
  — the requested functional reference.
- [LionHeartP/hyprlandRPM](https://github.com/LionHeartP/hyprlandRPM) — SCM
  source configured by that COPR. Its tree mixes Hyprland packages with
  Noctalia and general desktop packages; it is a fork of
  `solopasha/hyprlandRPM` and had no root license file in the reviewed tree.
- [nett00n/hyprland-copr](https://github.com/nett00n/hyprland-copr) — an
  alternative automation-oriented implementation licensed GPL-3.0. It is useful
  as a design reference but has a much wider package scope than this project.
- [Hyprland installation documentation](https://wiki.hypr.land/Getting-Started/Installation/)
  — currently points Fedora users at the LionHeartP COPR and lists the common
  overlay applications.

The public COPR API reported that the reference project follows Fedora
branching, automatically prunes, builds Fedora 43/44/45 and Rawhide for
`x86_64` and `aarch64`, and uses SCM/`rpkg` for most maintained packages. Its
package list also confirms why a fork must be pruned: it contains Noctalia,
Quickshell, Waypaper, Kitty, Waybar, Python helpers, and other non-Hyprland
content.

## Fedora and COPR documentation

- [COPR user documentation](https://docs.pagure.org/copr.copr/user_documentation.html)
  — authentication, source types, SCM packages, build batches, Fedora Review,
  manual repository creation, subprojects, and webhooks.
- [Reproducing COPR builds locally](https://docs.pagure.org/copr.copr/user_documentation/reproducing_builds.html)
  — reproducing a builder task with `copr-rpmbuild`.
- [Enabling a COPR repository](https://docs.pagure.org/copr.copr/how_to_enable_repo.html)
  — user-side repository enablement.
- [Fedora RPM Packaging Guide](https://rpm-packaging-guide.github.io/) — RPM and
  spec-file fundamentals.
- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
  — authoritative Fedora package policy.
- [Fedora legal allowed licenses](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/)
  — license eligibility for Fedora/COPR content.
- [COPR SCM source methods](https://docs.pagure.org/copr.copr/user_documentation.html#scm)
  — behavior of `rpkg` and `make_srpm`, including source-stage execution of
  `.copr/Makefile`.

COPR explicitly discourages building the same Version-Release as a package in
Fedora. It also documents build batches and manual repository creation; both
are central to publishing this ABI-coupled stack safely.

## Fedora package overlap

- [Hyprland in Fedora](https://packages.fedoraproject.org/pkgs/hyprland/)
- [hyprutils in Fedora](https://packages.fedoraproject.org/pkgs/hyprutils/)
- [hyprlang in Fedora](https://packages.fedoraproject.org/pkgs/hyprlang/)

These pages demonstrate that the COPR is an overlay over official Fedora
packages, not a fill-only repository. The complete overlap must be queried for
each target at implementation time.

## Reuse and licensing

- [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
  — explains that a public repository without a license remains subject to
  default copyright restrictions, while GitHub's terms permit viewing and
  forking through the service.
- [GitHub Terms: license grant to other users](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#5-license-grant-to-other-users)
  — defines the platform-level permission for public forks.

This is why the plan distinguishes “forking on GitHub” from importing,
modifying, and redistributing packaging files as a new open-source project.
Request clarification from the reference maintainer or implement independently
from licensed upstream sources and Fedora package references.
