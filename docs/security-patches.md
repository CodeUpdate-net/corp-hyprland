# Downstream security patches

These changes are included in release set `2026-09-19.1`. They are downstream
hardening; no CVE assignment or comprehensive upstream security certification is
claimed. See [security-audit.md](security-audit.md) for the broader audit process.

## hyprcursor-util: shell quoting (existing patch, retained)

[`0001-quote-xcur2png-input-path.patch`](../packages/hyprcursor/0001-quote-xcur2png-input-path.patch)
was present before this review. Cursor paths are interpolated into a shell
command invoking `xcur2png`. A literal apostrophe could terminate the original
single-quoted argument. The patch uses a shell-quoting helper that escapes each
apostrophe and quotes the complete canonical pathname.

The new extraction regression test exercises an apostrophe-containing filename.
This is a regression check for argument handling, not a general shell parser
security proof. The converter still invokes an external program through a shell.

## hyprcursor-util: private extraction directories (new)

[`0002-private-extraction-directory.patch`](../packages/hyprcursor/0002-private-extraction-directory.patch)
is introduced in `hyprcursor-0.1.13-3`. Previously, conversions shared the
predictable `/tmp/hyprcursor-util` directory and ran `rm -f` on its contents.
Another local process could pre-create that path as a symlink; simultaneous
conversions could also remove or mix each other's intermediate files.

The patch allocates a unique `mkdtemp` directory per cursor with mode 0700,
fails if allocation fails, preserves shell quoting, removes the shared-path
shell deletion, and uses scoped C++ cleanup on normal returns and stack
unwinding. It changes the conversion utility, not the cursor library ABI.
Abrupt process termination can leave a private directory behind; this is not
claimed to provide cleanup after SIGKILL or power loss. It does not audit all
archive/image decoders or make arbitrary cursor files safe.

[`test-extraction.py`](../packages/hyprcursor/test-extraction.py) runs in RPM
`%check` against the compiled utility. It uses a controlled fake `xcur2png` to
verify quoted filenames, private directory mode, successful and error-path
cleanup, and preservation of a sentinel behind a pre-existing shared-path
symlink. It passed local Fedora 44/45 builds and signed COPR build
[11004546](https://copr.fedorainfracloud.org/coprs/build/11004546/).

## Plugin ABI dependency hardening (new)

[`hyprland-plugins.spec`](../packages/hyprland-plugins/hyprland-plugins.spec)
release `0.56.0-3` replaces a broad compositor dependency with exact matching
build and runtime requirements for `hyprland = 0.56.2-4` on each Fedora target.
Plugins execute inside the compositor and use its internal interfaces;
installing an incompatible compositor can cause unresolved symbols or crashes.
The pin prevents that dependency combination through normal RPM transactions.
It is an ABI consistency guard, not isolation of plugin code or a fix for all
possible compositor crashes. Future Hyprland releases must rebuild the plugins
and update both pins together.

Static checks enforce these requirements. Signed COPR build
[11004547](https://copr.fedorainfracloud.org/coprs/build/11004547/) passed on both
targets; candidate installation tests verified the exact runtime dependency.
Runtime evidence is recorded in the release manifest and validation report.

## Packaging and validation safeguards

The same review made RPM checks mandatory with a Fedora Podman fallback,
verified source hashes and build-system files before builds, added traversal
checks for inspected archive members, and rejected unexpected scriptlet and
build-network patterns. Binary builds run offline as a nonroot container user.
These reduce packaging mistakes and build exposure; pattern checks cannot prove
that arbitrary build scripts or upstream source are harmless.

Do not drop these patches solely because an upstream version changes. Check
whether the underlying fixes landed upstream, rerun the regression tests, and
record the upstream commit that supersedes each downstream patch.

## Candidate 2026-10-11.1

Lua 5.5.1-2 backports the production hunks from upstream
[`0b29f408`](https://github.com/lua/lua/commit/0b29f408433e92953cc72b1d3e06c7ac8139e439).
The GC major/minor transition now guards negative memory deltas before parameter
arithmetic. An assertion documents the arithmetic function's precondition.
The ordinary GC smoke check does not reproduce the reported flaw. Fedora 45's
Hyprland uses system Lua, so this lua55 patch alone does not establish coverage
of that compositor's runtime. Signed Fedora source inspection confirmed the
missing upstream guard in `lua-5.5.1-2.fc45`; remediation is required before
publication.

Glaze 7.9.1-1 defaults the installed optional Asio download selector to OFF.
It can resolve system Boost/Asio when called, or fail when none is available.
This avoids an implicit FetchContent download in downstream distro builds.
It is a packaging safeguard, not a networking runtime security certification.

See [the current review](validation-2026-10-11.md) for source checks, upstream
parser/file-handling fixes, rebuild scope and validation limitations.

## Parallel Lua isolation in publication repair 2026-10-11.2

Lua55 5.5.1-4 keeps the reviewed GC backport and gives its 157 public C exports
private names through [lua55-prefix.h](../packages/lua55/lua55-prefix.h).
The installed headers preserve source API spelling; the binary ABI deliberately
changes to `liblua5.5.so.1`. Hyprland 0.56.2-7 and plugins 0.56.0-6 rebuild against
this ABI, with exact compositor pins and a minimum Lua55 release dependency.
Native Fedora Lua remains unchanged for Fedora's own consumers.

The original SONAME-only arrangement exported the same unversioned function
names as native Lua. Actual loader traces showed libinput resolving its calls
to the parallel runtime on both targets, crossing Lua 5.4/5.5 ABIs on Fedora 44.
This downstream fix prevents that collision for the reviewed public API; it does
not make arbitrary native C modules safe to load. Native modules used with Lua55
must compile against `lua55-devel`. The package's ordinary mixed-runtime test
uses independent native/private states in both global loader orders and rejects
native API exports. Actual VM qualification also checks the compositor's private
bindings and libinput's native bindings, alongside a running Lua configuration.

The same repair adds `/usr/bin/nm` to the compositor's runtime dependencies.
Its plugin API uses GNU nm for hook discovery; minimal install tests must check
that binutils is installed automatically. Compiler-equipped build roots alone
cannot establish that runtime dependency coverage.

Fedora 45's native `lua-libs-5.5.1-2` still lacks the GC guard. An ordinary state
probe confirmed its default collector is incremental. Actual libinput loader
bindings contain no `lua_gc` reference, and the
[official libinput sandbox API](https://wayland.freedesktop.org/libinput/doc/latest/lua-plugins.html)
excludes `collectgarbage`. Together with the verified guard's placement in the
generational major/minor transition, this supports the limited inference that
the reviewed libinput path does not switch into that affected mode. It is not a
fix or a general security certification for system Lua or other Fedora consumers.
See the exact probe and binding evidence in the release record.
