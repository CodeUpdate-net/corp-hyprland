# Publication repair, 2026-10-11.2

This authorized publication repair supersedes the blocked Git-only candidate
`2026-10-11.1`. Targets remain Fedora 44 and 45, x86_64. The current candidate
is Lua55 5.5.1-4, Hyprland 0.56.2-7 and plugins 0.56.0-6, with Glaze 7.9.1 and
its two rebuilt GUI consumers. Publication remains gated on the exact signed
candidate; see [the release record](../releases/2026-10-11.2.json).

## Runtime and security fixes

Hyprland requires `/usr/bin/nm`: its verified PluginAPI.cpp invokes GNU nm for
hook discovery. Compiler-equipped build images masked this missing runtime
dependency. Minimal runtime installs must prove that the dependency installs
binutils automatically. Plugins pin the exact compositor version and release.

Hyprland selects patched parallel `lua55 >= 5.5.1-4` on both targets. The upstream
GC backport and ordinary incremental/generational regression tests remain in
place. Fedora's native Lua remains installed for its own consumers, including
libinput; this release does not claim to patch Fedora's system Lua.

A separate SONAME alone did not isolate the original runtime's unversioned C
symbols. Actual dynamic-loader traces showed libinput resolving native Lua API
calls to the parallel library, including Lua 5.4 calls to Lua 5.5 on Fedora 44.
Lua55 release 4 prefixes all 157 public API exports and changes the SONAME to
`liblua5.5.so.1`. Installed headers map the usual source API names to the private
exports. Hyprland and its plugins are rebuilt against these headers. Other native
C consumers/modules must also rebuild against `lua55-devel` to use this ABI.

The package checks reject native API exports and create independent native and
parallel Lua states in both global loader orders. These targeted checks pass on
both targets. Signed VM tests must additionally prove that configuration uses
the patched private runtime while libinput resolves its own native Lua symbols.
Glaze 7.9.1 remains within the verified compositor CMake 7.x requirement.

## Preserved rejected attempt

The initial signed candidate (Lua55 release 3, Hyprland release 6, plugins
release 5) passed all 29 local builds on both targets, signed artifact/source
inspection and six fresh/upgrade cases. Actual VMs failed plugin hook discovery
because nm was absent. Adding nm only for diagnosis allowed all four plugins,
wallpaper, the Glaze GUI consumers, idle/resume and lock/PAM checks to run, then
exposed the Lua symbol collision. These diagnostic results do not qualify the
shipping candidate. No repository regeneration occurred. Evidence is retained
in [the rejected attempt record](../releases/2026-10-11.2-attempt-1.json).

The subsequent nm-only full builds were interrupted before COPR submission when
the Lua ABI collision was confirmed. Their logs and frozen inputs are retained.
The first isolated-Lua prototype failed because its test tried to resolve
`luaL_openlibs`, a macro in Lua 5.5. The corrected test uses exported
`luaopen_base`; both complete targeted builds then passed.

## Qualification scope

Fresh full offline nonroot builds of all 29 packages, repository checks,
exact signed candidate inspection, installs/upgrades and VM session tests are
being repeated for the final frozen inputs. Three unchanged changed-package
recipes (Glaze, shutdown and systeminfo) retain their signed builds from
immutable commit 91d51a5; Lua55, Hyprland and plugins require new builds. Each
build's recipe commit is recorded. The other 23 packages inherit exact signed
builds from the previous public release.

Fresh native Fedora repository queries found no compositor/devel RPM on either
target. That compositor upgrade origin is not applicable, with query evidence
recorded. Transitions from every available native Hypr library/devel package and
system Lua, and from the complete previous public COPR set, remain required.

Runtime qualification uses disposable KVM guests with real local PAM/logind
sessions, plugin rendering/hook tests, configuration reload, wallpaper, idle,
lock/unlock, polkit cancellation/failed/successful authentication, and a real
portal chooser/PipeWire stream. Physical GPUs, HDR, multi-monitor operation,
hardware suspend and game workloads are not established by this coverage.
COPR remains in manual publication mode with binary networking disabled.
