# Package scope

## Inclusion test

A source package belongs in this COPR only when all answers are **yes**:

1. Is it maintained under the `hyprwm` upstream organization, or is it a direct
   build/runtime dependency of an included `hyprwm` project?
2. Is Fedora's package missing, too old for the selected Hyprland release, or
   ABI-incompatible with the release set?
3. Can it be built from redistributable, pinned sources without downloading
   code during `%build`?
4. Will the maintainer test it on every required target?

First-party applications may be included even when not strictly required by
the compositor. Third-party applications whose names merely begin with
“hypr” do not qualify automatically.

## MVP inventory

The inventory is a policy target, not a claim that every dependency must be
overridden on every Fedora release. During implementation, compare each target
Fedora package against the minimum versions from the selected Hyprland tag.

### Release-set core

These packages are ABI-sensitive or form the build foundation. If one is
overridden, rebuild its downstream consumers in the same release set.

| Source package | Role | MVP disposition |
| --- | --- | --- |
| `hyprland-protocols` | Hyprland-specific Wayland protocol definitions | Include when Fedora is missing/older. |
| `hyprwayland-scanner` | Protocol code generator | Include when Fedora is missing/older. |
| `hyprutils` | Shared utility library | Include in the coherent set. |
| `hyprlang` | Configuration language library | Include in the coherent set. |
| `hyprgraphics` | Shared graphics library | Include in the coherent set. |
| `hyprcursor` | Cursor format/library | Include when required by the selected tag. |
| `hyprwire` | Hyprland IPC/serialization library | Include when required by the selected tag. |
| `aquamarine` | Display/backend library used by Hyprland | Include in the coherent set. |
| `hyprtoolkit` | First-party UI toolkit | Include when consumed by selected applications. |
| `hyprland` | Stable compositor and development files | Always include; this is the anchor package. |
| `hyprland-plugins` | Official plugins | Include and build after the matching Hyprland NEVR. |

### First-party session applications

These are in initial scope, but an application can be deferred from the first
publish if upstream does not have a stable tag or a required dependency cannot
yet meet the packaging gates.

| Source package | Function |
| --- | --- |
| `xdg-desktop-portal-hyprland` | Desktop portal backend |
| `hypridle` | Idle daemon |
| `hyprlock` | Screen locker |
| `hyprpaper` | Wallpaper daemon |
| `hyprpicker` | Wayland color picker |
| `hyprsunset` | Color-temperature utility |
| `hyprpolkitagent` | Polkit authentication agent |
| `hyprland-qt-support` | Qt/QML style support |
| `hyprqt6engine` | Qt 6 theme engine |
| `hyprland-guiutils` | Shared Hyprland GUI utilities |
| `hyprlauncher` | First-party launcher |
| `hyprpwcenter` | Audio management UI |
| `hyprshutdown` | Session shutdown utility |
| `hyprsysteminfo` | System information utility |
| `hyprland-contrib` | Community scripts hosted by `hyprwm`; defer if no stable tag satisfies the stable-only policy. |

Package names and upstream ownership must be revalidated when implementation
starts; the Hyprland ecosystem changes quickly.

### Conditional compatibility packages

Do not add these preemptively. Add one only when a clean target build proves it
is necessary and the exception is documented in the package directory.

- A versioned or compatibility build of `glaze` if Hyprland pins a range Fedora
  cannot provide. Prefer parallel-installable paths over replacing Fedora's
  general-purpose package.
- Any toolchain compatibility package required by a current stable Hyprland
  tag. It must not leak into unrelated system packages.
- Bundled source permitted by Fedora policy when no safe system alternative
  exists; declare the appropriate `Provides: bundled(...)` metadata.

## Explicit exclusions

- All Noctalia packages, meta packages, greeters, configuration, and legacy
  variants.
- `quickshell`, `matugen`, `waypaper`, `waybar-git`, `kitty`, `qt6ct`, `uwsm`,
  `cliphist`, `awww`, `mpvpaper`, `gpu-screen-recorder`, fonts, and generic
  desktop tooling.
- Python helper packages brought in only for Noctalia or Waypaper.
- Third-party utilities such as `hyprshot`, `hyprnome`, `hyprdim`, Pyprland,
  and workspace-name scripts. They can be revisited in a separate “extras”
  project, not this COPR.
- `wlroots` and `wayland-protocols` overrides unless a selected first-party
  package demonstrates a hard version requirement Fedora cannot meet.
- `hyprland-git` and `hyprland-plugins-git` in the production project.

## Fedora overlap policy

Fedora currently carries Hyprland and several core libraries. This COPR is
allowed to override those packages because delivering a newer Hyprland is its
purpose, but it must follow these rules:

- never publish the same Version-Release as Fedora;
- prefer a newer upstream `Version` rather than artificially racing Fedora's
  `Release` field;
- preserve `Epoch` if Fedora's package already defines one;
- compare the complete EVR for every supported Fedora release before promotion;
- verify both `dnf upgrade` into the COPR and `dnf distro-sync` after disabling
  it;
- remove an overlay dependency once all supported Fedora targets provide a
  suitable version and no coherent rebuild requires it.

## Dependency waves

The exact graph must be generated from the chosen specs with
`rpmspec -q --buildrequires`. The expected initial waves are:

1. Protocol definitions, scanner, `hyprutils`, and any approved compatibility
   dependency.
2. `hyprlang`, `hyprgraphics`, `hyprcursor`, and `hyprwire`.
3. `aquamarine`, `hyprtoolkit`, and Qt support libraries.
4. `hyprland`.
5. First-party applications.
6. `hyprland-plugins`, built against the published Hyprland development files.

If the parsed BuildRequires graph disagrees, the graph wins and this document
must be updated.

## Fork-pruning map

If the owner chooses a GitHub fork after the reuse-license gate is resolved,
use an allowlist instead of trying to maintain a growing denylist.

Retain only the packaging for:

```text
aquamarine                         hyprland-plugins
glaze (conditional)                hyprland-protocols
hyprcursor                         hyprland-qt-support
hyprgraphics                       hyprlang
hypridle                           hyprlauncher
hyprland                           hyprlock
hyprland-contrib (conditional)     hyprpaper
hyprland-guiutils                  hyprpicker
hyprpolkitagent                    hyprpwcenter
hyprqt6engine                      hyprshutdown
hyprsunset                         hyprsysteminfo
hyprtoolkit                        hyprutils
hyprwayland-scanner                hyprwire
wayland-protocols (conditional)    xdg-desktop-portal-hyprland
```

The reference repository generates stable `hyprland` from its
`hyprland-git/hyprland-git.spec`. In this project, split that into a normal
`packages/hyprland/hyprland.spec` which contains no snapshot mode. Do the same
for plugins. Retain `glaze` or `wayland-protocols` only if the target audit
proves Fedora cannot satisfy the selected stable release.

Replace the root README and audit/rewrite `.copr/Makefile` and all CI workflows;
their existing logic covers packages that are out of scope. Delete every other
package directory, then verify the COPR package list itself has no stale
definitions left. Removing a directory from Git does not remove its package
entry or old RPMs from COPR.
