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

Checks are in progress. Results, exact artifact/signature evidence, dependency
and upgrade transactions, actual runtime coverage and remaining limits belong
in [the release record](../releases/2026-10-11.2.json). COPR remains in manual
mode with build networking disabled. No regeneration occurs until the
required prepublication checks pass.


Fresh native repository queries on both targets find the Hypr libraries and
system Lua but no `hyprland` or `hyprland-devel` package. The Fedora compositor
upgrade origin is therefore not applicable; it is not recorded as passed.
The Fedora transition test will install all available native Hypr libraries/
devel packages plus system Lua, then install the complete signed candidate.
The full previous-public-COPR upgrade remains a separate required gate.
