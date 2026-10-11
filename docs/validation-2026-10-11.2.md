# Publication repair, 2026-10-11.2

This candidate supersedes the blocked Git-only candidate `2026-10-11.1`.
Publication to `dtutila/hyprland` is authorized. Supported targets remain
Fedora 44 and 45, x86_64.

## Lua remediation

The previous review found that Fedora 45 system Lua lacks the upstream GC fix.
Hyprland now selects the already backported parallel `lua55` runtime on both
targets and requires `lua55 >= 5.5.1-3` at build and runtime. This uses the
separate `liblua5.5.so.0` library and versioned headers; it leaves Fedora's
system Lua available for its other consumers. Hyprland devel metadata exports
`lua55` so plugins compile against the same runtime. Hyprland is rebuilt as
0.56.2-6, and plugins as 0.56.0-5 with exact compositor pins.

The verified Hyprland CMake source tries `lua55` before all system Lua module
names. All source archives and production patches from the upstream review are
unchanged. Glaze 7.9.1 remains within the compositor's required 7.x range.

## Validation and publication

Repository checks and full offline nonroot Podman builds passed on both
targets: all 29 packages built, all 89 binary RPMs installed, `dnf check` passed
and RPM lint reported zero errors. Metadata/security inspection of all 38
runtime/devel RPMs per target found no setuid/setgid, file-capability or unexpected
world-writable files, and no new scriptlets. Both Hyprland RPMs and plugins require
`liblua5.5.so.0`; plugins pin the compositor exactly at 0.56.2-6. All 74 tracked
recipe inputs and 29 selected archive digests match the immutable source commit
`91d51a517c713dfa6b09812ebe7f9aa2462166b6`, whose GitHub CI also passed.

COPR builds, signatures, upgrades and full-session tests are pending. Results,
exact artifact/signature evidence, dependency and upgrade transactions, actual
runtime coverage and remaining limits belong in [the release record](../releases/2026-10-11.2.json). COPR remains in manual
mode with build networking disabled. No regeneration occurs until the
required prepublication checks pass.


Fresh native repository queries on both targets find the Hypr libraries and
system Lua but no `hyprland` or `hyprland-devel` package. The Fedora compositor
upgrade origin is therefore not applicable; it is not recorded as passed.
The Fedora transition test will install all available native Hypr libraries/
devel packages plus system Lua, then install the complete signed candidate.
The full previous-public-COPR upgrade remains a separate required gate.
