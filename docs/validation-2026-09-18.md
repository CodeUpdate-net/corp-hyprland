# Packaging validation record — 2026-09-18

Review started 2026-09-18; final results verified 2026-09-19.

Baseline reviewed: Git commit `5617928d23b405474454756774e1169594e7f8cc`,
release set `2026-09-18.1`. The working-tree fixes described below are not yet
committed, submitted to COPR or published. This record distinguishes the public
release from local candidate validation.

## Setup verified

- Public COPR API: `devel_mode=true`, `enable_net=false`; only
  `fedora-44-x86_64` and `fedora-45-x86_64` are configured. The backend is Pulp.
- Recent COPR builds for the updated packages succeeded on both configured
  targets, including corrected hyprland-protocols build **11002501**, Hyprland
  **11002509**, and plugins **11002517**. The earlier protocol build **11002473**
  failed. The corrected public protocol RPM is 0.7.1-1.
- `git ls-remote origin HEAD` succeeds with `id_ed25519_dtutila` and matches the
  baseline commit. The key is now pinned in this repository's local Git config.
  No push was performed, so write access was not independently tested.
- Both Claude memory notes exist. Their workflow is now captured in tracked
  docs; the old `.pub` SSH identity example differs from the verified command.
- libsecret belongs in `dtutila/utils`; it is absent from this manifest.

API evidence: [project configuration](https://copr.fedorainfracloud.org/api_3/project?ownername=dtutila&projectname=hyprland),
[build list](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/builds/).

## Checks completed

- 29 Python regression tests pass, including CMake/Meson source detection,
  checksum/path validation, trigger-scriptlet rejection, manifest dependencies
  and exact plugin ABI pins.
- All 29 pinned source archives match SHA-256 and the spec's upstream build
  system. These checks inspect the archive without extracting its contents.
- All 29 specs parse and lint in both dedicated Fedora 44 and Fedora 45 images.
  Lint retains warnings for packages with no `%check` suite.
- Fresh public-repository installations on both Fedora targets include all
  available runtime/devel packages, with signature checking enabled; `dnf check`
  succeeds. Hyprland reports **0.56.2**, hyprctl prints help, and hyprcursor-util
  reports **0.1.13**. Hyprland needs a mode-0700 `XDG_RUNTIME_DIR` even for its
  version command. hyprctl's help command returns 1; the harness handles that
  expected help status explicitly.
- Prior scratch results show 29/29 Fedora 44 package builds and installs. Their
  89 binary RPMs were independently re-linted: zero errors after the narrow,
  reviewed filters; 34 warnings remain. These prior results are supporting
  evidence, not builds of the new audit fixes.
- All 38 public runtime/devel packages on Fedora 44 were inspected for RPM
  scriptlets, setuid/setgid bits, world-writable nonsymlink paths and file
  capabilities: none were found.
- A clean-cache protocol source download succeeds with the new downloader.
- A complete saved Fedora 44 package set upgrades to the public COPR release
  and passes `dnf check`: Hyprland 0.56.2-2 to 0.56.2-4, Hyprtoolkit 0.5.4-3 to
  0.6.0-1, hyprutils 0.14.1-2 to 0.14.2-1, and hyprpolkitagent 0.1.3-1 to
  0.2.0-1. The baseline uses saved local RPMs; the upgrade uses signed COPR RPMs.
- Shell syntax, Python compilation and `git diff --check` pass.

## Candidate changes

- Mandatory RPM checks with a Fedora Podman fallback, upstream build-system
  validation, target-specific CI, and a failure-propagating offline build runner.
- hyprcursor **0.1.13-3**: private extraction directories and a regression test
  covering quoting, symlink isolation, mode 0700 and cleanup on success/failure.
- hyprland-plugins **0.56.0-3**: exact build/runtime pin to Hyprland **0.56.2-4**.
- Versioned build/test/publish/security documentation and the actual architecture
  matrix. The former `docs/` ignore rule is removed.

## Full candidate build results

Both complete runs passed: **29/29 source packages**, producing **89 binary
RPMs per target**, built offline as an unprivileged user, then installed and
linted. The final RPM lint result is **0 errors, 34 warnings** per target after
the reviewed filters. The cursor extraction regression passes on both targets.

| Target | Result directory under `results/` | Outcome |
| --- | --- | --- |
| Fedora 44 x86_64 | `fedora-44-20260919T002551Z-cacb599d` | Passed |
| Fedora 45 x86_64 | `fedora-45-20260919T002937Z-8968c84f` | Passed |

Each directory contains `result.json`, `inputs/`, `rpms/`, `srpms/`, package
logs, `install.log` and `rpmlint.log`. Package build inputs were compared with
the final checkout: no code, spec, patch, test or archive changes occurred
between these builds and the final review. Package README documentation was
updated separately and is not an RPM build input.

The previous-to-current release upgrade also passed on **Fedora 45**, using
all 29 historical COPR builds selected before the September 18 update. Both the
historical installation and public upgrade kept COPR signature checks enabled.
Hyprland upgraded from 0.56.2-3 to 0.56.2-4; Hyprtoolkit, hyprutils and the polkit
agent reached the same current versions as Fedora 44, and `dnf check` passed.
Historical baseline examples: Hyprland build 10933716, Hyprtoolkit 10933507,
hyprutils 10933493 and hyprpolkitagent 10933345.

Upgrade evidence concerns the previous-to-current **public** release. The new
local audit-fix RPMs have passed clean builds and installs but are not yet signed
or published through COPR.

## Limits and required pre-publication gates

The enabled Fedora repositories offered no `hyprland` package on either target
when the upgrade baseline was requested. A Fedora-to-COPR compositor upgrade
could not be exercised; it is not counted as a pass. Previous-release upgrades
passed on both targets as described above.

A nested/VM desktop session, actual plugin loading, GPU paths, screen-sharing,
lock/unlock and polkit authentication were not exercised by the containers.
A clean Mock run and complete upstream advisory review remain release gates.
No claim is made that all upstream source code is vulnerability-free.

The GitHub security pages consulted for
[Hyprland](https://github.com/hyprwm/Hyprland/security),
[hyprlock](https://github.com/hyprwm/hyprlock/security), and
[hyprpolkitagent](https://github.com/hyprwm/hyprpolkitagent/security)
showed no published advisories in the retrieved pages; some results were cached.
The hyprcursor security page could not be retrieved. These limited checks are
not a complete or live CVE assessment.

Do not regenerate COPR metadata for these local fixes until new signed builds
and the required release gates are reviewed. Manual publication remains enabled.
