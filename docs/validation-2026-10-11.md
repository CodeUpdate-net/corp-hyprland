# Upstream review and candidate validation, 2026-10-11

Candidate: `2026-10-11.1`, branch `release-set/2026-10-11.1`.
Previous published Hyprland set: `2026-09-19.1`.
Targets: Fedora 44 and 45, x86_64.

## Upstream inventory

All 29 manifest repositories were checked through fresh Git tag advertisements
and GitHub's latest-release endpoint. Existing numeric release tags resolve to
the recorded source commits. UWSM and hyprland-plugins return HTTP 404 for the
latest-release endpoint; their successfully retrieved Git tags establish their
latest stable versions instead. Development branches were not selected.
The [inventory](../releases/upstream-review-2026-10-11.json) records each repository,
tag, commit, decision and public advisory query result.

Glaze has newer releases. The candidate selects [7.9.1](https://github.com/stephenberry/glaze/releases/tag/v7.9.1),
the highest stable 7.x tag, because the verified Hyprland 0.56.2 archive requires
`find_package(glaze 7...<8)`. Glaze 8.x and 9.x are outside that range. No other
manifest package has a newer stable numeric tag. GNOME's top-level and 0.21
release indexes still identify libsecret 0.21.8.2 as latest; its recipe remains
in the separate `dtutila/utils` project.

## Source and security review

The Glaze tag resolves to `cadcadea26554cc4214769e358f981426e40a02a`.
Its HTTPS archive SHA-256 is
`d6dee391276f5375672c35d06058e4fd8f1f30f62bae163a004b3bd13a4e2ae3`.
The verified archive contains the expected root CMake build, declares version
7.9.1, retains C++23 and the header-only target, and installs under the existing
include/share paths. The Glaze MIT license file is byte-identical to 7.2.0,
but the newly installed `FindAsio.cmake` module declares BSD-3-Clause. The
RPM license is therefore `MIT AND BSD-3-Clause`, and the referenced CMake
license text is included. The new adapted zmij formatter retains its copyright
notice and now includes its MIT license text. Bundled fast_float and zmij
code are declared in the devel RPM; no unsupported upstream version is claimed.
The extra license texts and local Glaze inputs have checksums in `sources`.

The [upstream diff](https://github.com/stephenberry/glaze/compare/v7.2.0...v7.9.1)
was reviewed with attention to installed CMake modules, JSON/binary parser
bounds, variant indices, filesystem reads, HTTP routing and consumer APIs.
Upstream fixes include bounds checks before binary variant selection, bounded
lazy JSON scans, decoded route traversal checks and short-read handling.
The file reader still obtains file size by pathname and does not provide a
general filesystem race-safety guarantee. HTTP fixes affect optional networking
headers; the Hyprland packages' JSON use does not establish networking coverage.
This focused review is not a line-by-line audit of the whole upstream change.

Glaze now installs an optional Asio setup module that can download a fallback
dependency. The downstream patch defaults that option to OFF, including for
installed CMake consumers. System Boost/Asio remains available to callers.
Developer mode, examples and SSL remain disabled; compilation is offline.
The new RPM check exercises ordinary typed/generic JSON reads and round trips
used by stack consumers. It does not run the complete upstream Glaze test suite.

All 29 GitHub public repository advisory endpoints returned HTTP 200, empty
lists and no pagination. However, [Lua's official bug list](https://www.lua.org/bugs.html#5.5.1-1)
reports undefined behavior in GC parameter arithmetic for 5.5.1.
The candidate backports the production changes from upstream commit
[`0b29f408`](https://github.com/lua/lua/commit/0b29f408433e92953cc72b1d3e06c7ac8139e439):
guard negative memory deltas and assert the arithmetic function's precondition.
The source archive and version remain 5.5.1; RPM Release becomes 2.
The check exercises ordinary incremental/generational collection and retained
values. It does not reproduce the reported flaw or provide sanitizer coverage.

Fedora 44 Hyprland uses the patched parallel lua55 library. Fedora 45 Hyprland
retains Fedora's system Lua dependency: this downstream patch does not establish
that the Fedora system package includes the fix. This remains a publication
blocker. A disposable Fedora 45 install selected `lua-libs-5.5.1-2.fc45`
from updates-testing; its August 27 changelog updates legacy Lua and does not
mention the September upstream GC fix. A subsequent nonroot, offline inspection
of the signed `lua-5.5.1-2.fc45.src.rpm` confirmed that the source retains the
unguarded GC call and does not include the upstream fix. The signature verified
against the Fedora validation image's installed public key
`4f50a6114cd5c6976a7f1179655a4b02f577861e`. The source was not executed and no
vulnerability reproduction was run. Remediate this dependency before publication. The existing hyprcursor shell quoting/private-directory patches
are retained. Empty public advisory lists are not a security certification.

Glaze is header-only, so Hyprland, hyprshutdown and hyprsysteminfo receive release
bumps and rebuilds. Hyprland's release is 5; hyprland-plugins is rebuilt at release
4 with exact build/runtime pins to `hyprland = 0.56.2-5%{?dist}`.

## Validation status

The required repository checks passed: `./scripts/check` used the Fedora 44
Podman fallback because native RPM validation tools were incomplete;
`FEDORA=45 ./scripts/check-container` also passed. Both ran 29 Python tests,
parsed/linted all 29 specs with zero lint errors, and verified archive checksums
and root build systems. Existing visible lint warnings remain documented.

Full offline nonroot container builds passed for all 29 packages on both
targets. Each full set contains 89 binary RPMs including debug packages and
29 source RPMs. The fresh container install and `dnf check` passed; binary
lint reports zero errors and 34 visible warnings on each target. The warnings
are retained rather than hidden by new lint filters.

After those inputs were frozen, Glaze received only a license/Provides metadata
correction and two extra license files. Its final targeted builds passed on both
targets. RPM payload inventories confirm all 294 header/CMake paths have the
same digests and modes as the Glaze RPMs used by the full consumer builds.
The final assembled sets use these corrected Glaze RPMs. Fresh disposable
installs verified all 89 artifact NEVRAs on each target, passed `dnf check`,
and repeated whole-stack lint with zero errors and the same 34 warnings.
The failed initial license-copy attempts are preserved and explained in the
candidate record; no lint exceptions were widened.

All current manifest and package recipe files match the final build inputs:
non-Glaze inputs match the full builds, and Glaze inputs match its corrected
builds. Build logs confirm Hyprland, hyprshutdown and hyprsysteminfo selected
local Glaze 7.9.1 on both targets. The built plugin RPMs require exactly
`hyprland(x86-64) = 0.56.2-5.fc44` or `.fc45`, respectively.

Inspection covered all 38 non-debug binary RPMs per target: Requires, Provides,
licenses, scriptlets, file modes and capabilities. No setuid/setgid files,
non-sticky world-writable paths, file capabilities or scriptlets were found.
Their RPM digest checks passed, as did all 29 source RPM digest checks per
target. These local RPMs are unsigned and were installed only in disposable
containers; this is not signed COPR artifact validation.

Exact artifact hashes, immutable image IDs, source-input hashes, log hashes,
results paths and the investigated failure are recorded in
[the candidate record](../releases/2026-10-11.1.json).
Desktop/plugin runtime, signed candidate install/upgrade, clean Mock builds and
fresh public metadata verification remain pending. Fedora 45's unfixed system
Lua dependency is a confirmed publication blocker. Build/install success does
not qualify desktop behavior. No COPR submission or repository regeneration
is part of this Git update.

Raw review and validation logs are preserved in `results/upstream-2026-10-11/`.

## Repeat the upstream review

For each manifest upstream, retrieve numeric stable Git tags and resolve
annotated tags to their commit. Compare version components numerically, then
check the latest-release endpoint and prerelease status. A missing GitHub
release object does not imply that tags are absent. Check compatibility ranges
in verified consumer source archives before selecting a library version.
Check GNOME's stable index separately for the utils libsecret recipe.

Query every public repository advisory endpoint, preserving HTTP status,
pagination and response; also consult upstream-specific bug/security lists,
including Lua's official bugs page. Empty GitHub advisories alone missed the
Lua fix found in this review. Record source and patch provenance, actual
coverage and limitations before pushing a candidate release branch.
