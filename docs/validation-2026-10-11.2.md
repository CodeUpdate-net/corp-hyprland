# Publication repair, 2026-10-11.2

Publication was requested at `2026-10-11T23:50:25.974541+00:00` and fresh public metadata and signed installs were verified on both targets at `2026-10-11T23:55:37.365658+00:00`. Targets are Fedora 44 and 45, x86_64. The
[release record](../releases/2026-10-11.2.json) contains exact revisions, RPM
hashes, signatures, transactions, build IDs and evidence paths. This release
supersedes the blocked Git-only candidate `2026-10-11.1` and upgrades the previous
public set `2026-09-19.1`.

The tested release was fast-forwarded into `main` and pushed. GitHub metadata
and Fedora 44/45 RPM checks passed for both `main` and the release-set branch.
Task VM processes, baseline images and ephemeral VM SSH files were removed;
raw logs, RPMs and VM disk evidence were retained. The integration and cleanup
details are in the release record.

## Reviewed sources and selected builds

The [upstream review](validation-2026-10-11.md) checked all 29 manifest
repositories. Glaze 7.9.1 is the newest reviewed compatible 7.x release; the
verified compositor CMake requirement excludes newer major versions. The Lua
5.5.1 GC production fix is backported from upstream. Source provenance, archive
checksums, build systems and licenses were reviewed together.

| Changed recipe | Version-release, before Fedora suffix | COPR build | Recipe commit |
| --- | --- | --- | --- |
| glaze | 7.9.1-1 | [11109404](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109404/) | 91d51a5 |
| lua55 | 5.5.1-4 | [11109682](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109682/) | da97869 |
| hyprland | 0.56.2-7 | [11109690](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109690/) | da97869 |
| hyprland-plugins | 0.56.0-6 | [11109743](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109743/) | da97869 |
| hyprshutdown | 0.1.1-3 | [11109410](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109410/) | 91d51a5 |
| hyprsysteminfo | 0.2.0-3 | [11109411](https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/build/11109411/) | 91d51a5 |

The final Lua55/compositor/plugin package source is immutable commit
`da97869f525f974ec1381233ac1b3ca6a9ff8d9d`. Glaze and its two GUI consumers reuse byte-identical
recipes from `91d51a517c713dfa6b09812ebe7f9aa2462166b6`. The other 23 packages
inherit the exact signed builds from the previous public set. Per-package
upstream revisions and packaging recipe commits are separate fields in the
record. No moving branch was submitted.

## Security and runtime fixes

Hyprland now requires `/usr/bin/nm`, which its verified plugin API invokes for
hook discovery. Independent minimal fresh installs began without nm on both
targets and proved binutils was installed automatically. Plugins require and
build against exactly Hyprland 0.56.2-7 for the matching Fedora distribution.

Both targets use patched parallel `lua55 >= 5.5.1-4` for compositor configuration.
A separate SONAME alone did not isolate the original runtime's unversioned C
symbols: actual loader traces showed libinput resolving native calls to parallel
Lua, crossing Lua 5.4/5.5 ABIs on Fedora 44. Release 4 prefixes all 157 public C
exports and changes the SONAME to `liblua5.5.so.1`. Headers preserve source API
spelling. Other C consumers/modules must rebuild against `lua55-devel` to use
this ABI. Package checks reject native API exports and exercise independent
native/private Lua states in both global loader orders.

Signed VM tests verified the running Lua configuration, compositor private
bindings and all 45 reviewed libinput bindings to native Fedora Lua. Fedora's
system Lua remains unchanged. Native Fedora 45 `lua-libs-5.5.1-2` still lacks the
GC guard; its ordinary state probe showed the default incremental collector.
The absence of `lua_gc` from reviewed libinput bindings and its sandbox's
excluded `collectgarbage` support a limited inference about that path, not a
system-wide fix. See [security-patches.md](security-patches.md) for exact scope.

## Completed qualification

- `./scripts/check` and `FEDORA=45 ./scripts/check-container` passed, including
  required Podman RPM checks. The metadata transport tool change was checked on
  both targets as well.
- Fresh full offline, nonroot Podman builds passed all 29 packages and produced
  89 binary/debug RPMs per target. Install/dependency checks passed; RPM lint had
  zero errors. Both runs had identical 106 frozen inputs, with 76 recipe files
  checked against the immutable package source and all 29 selected archives
  verified. No host credentials, home, display or D-Bus were exposed to source
  compilation.
- All six changed recipes passed actual clean COPR Mock builds on both targets:
  12 distinct fresh roots, binary networking disabled and exact dependency
  selections inspected. Managed Mock dependency logs can contain NOKEY warnings;
  they are not claimed as strict signature verification.
- The exact candidate's 89 binary and 29 source RPMs per target passed strict
  project-signature and digest checks using fingerprint
  `0172D569420212CE7D0D93E2EB8806A8E4BB2A44`. All 29 extracted source bundles were
  compared offline as a nonroot user to committed recipes and archive hashes.
- All 38 runtime/devel RPMs per target were inspected for Provides, Requires,
  scripts, permissions, capabilities and licenses. There were no permission
  anomalies or new scriptlets. The inherited Qt support RPM's recorded private
  Qt 6.11 dependency difference from current local builds was separately
  reviewed and satisfied by actual installs.
- Four exact signed transactions per target passed: fresh, complete previous
  public set, available native Fedora components/system Lua, and minimal fresh
  runtime. All 38 expected RPMs were present, with `dnf check`, no unexpected
  removals and no downgrades. Existing native system Lua was retained. Fresh Fedora
  queries found no compositor/devel RPM on either target, so that specific
  upgrade origin is recorded as not applicable rather than passed.
- Fresh development metadata selected the latest packages by name and delivered
  all 38 exact tested signed RPM hashes on both targets. Candidate RPM files were
  not mounted into those repository-download tests.
- Disposable KVM guests, using verified signed Fedora cloud images and actual
  local PAM/logind sessions, passed the signed candidate desktop tests on both
  targets. Coverage includes all four plugins loading/rendering/unloading,
  configuration reload with client survival, wallpaper, systeminfo and shutdown
  GUI consumers, idle/resume, wrong/correct lock authentication, polkit cancel,
  wrong-password PAM failure and successful authentication, and the real portal
  chooser followed by three nonblack PipeWire frames. Dynamic-loader evidence
  verified the private/native Lua ownership. Screenshots and session/service
  logs were inspected.

The guests upgrade the preserved rejected first candidate. Separately installed
diagnostic nm is disclosed; the independent minimal container cases establish
automatic dependency installation. Helpers use a dedicated real graphical
session target and handle the chooser during SelectSources, matching the
verified portal source. Authentication evidence is correlated to test timestamps.

## Preserved failures and limits

The publication command queues metadata regeneration. The first public checks
still received previous-release metadata and rejected those downloads before
installation. Both failed attempts were preserved; after both metadata hashes
advanced, fresh latest-package downloads and signed install checks were repeated.
The publication record separates the request time from verification time.


The first signed candidate (Lua55 release 3, Hyprland release 6, plugins release
5) passed builds and container transactions but failed actual VM hook discovery
without nm. Diagnostic nm then exposed Lua symbol interposition. No repository
regeneration occurred for that attempt. Its results, later diagnostics and
relocation maps are retained in the
[rejected attempt record](../releases/2026-10-11.2-attempt-1.json). Older versions
remain normal COPR build/repository history; qualification checks latest package
selection against the newer exact signed candidate.

The nm-only local builds were stopped before COPR once the ABI collision was
confirmed. The initial namespace prototype's test incorrectly resolved a Lua
5.5 macro; the corrected test uses exported `luaopen_base`, and both targeted
builds passed. All failed logs and frozen inputs are retained.

The first final-candidate VM suites completed the runtime actions, but log review
found an obsolete `general:grace` option in the lock fixture. The option was
removed and a configuration-error assertion added. Both complete suites passed
again with the same signed RPMs; the first fixture evidence remains under each
guest's `obsolete-lock-fixture/` directory.

The first chooser screenshot raced its first rendered frame despite successful
selection and capture. Explicit picker focus and a render delay were added; both
complete suites passed again, preserving prior evidence under
`portal-screenshot-timing/`. The first added focus call used obsolete dispatcher
syntax and failed both tests; it was corrected to the already-tested Lua
dispatcher. Failed evidence remains under `portal-focus-syntax-failure/`.

The final Fedora 45 full build encountered a stalled mirror zchunk transfer.
Its failed preparation and DNF logs were preserved. The resumed run used full
metadata through `--no-zchunk`, after verifying unchanged frozen inputs, base
image and every completed RPM checksum. Source builds remained offline/nonroot;
RPM signature policy was unchanged. See the reusable
[retry procedure](build-and-test.md#retry-a-interrupted-build).

Physical GPUs, HDR, multiple monitors, hardware suspend and game/Vulkan workloads
were not qualified. Unchanged uwsm, hyprshot, hyprpicker, hyprsunset, launcher,
audio-center and Qt engine did not receive separate full functional session
qualification. Successful checks do not establish exhaustive desktop/plugin
correctness or system-wide security. COPR manual publication remains enabled
and binary build networking remains disabled. Users should restart their session
after updating the stack.
