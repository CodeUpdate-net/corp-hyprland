# Nested desktop and plugin tests

Use this after signed candidate installs pass, before COPR publication. This
runs real Hyprland, clients and plugins in disposable Fedora containers on an
existing Wayland desktop. The nested compositor has a private D-Bus session and
runtime directory. It does not replace the host compositor or install host RPMs.

`runtime/smoke.py` checks compositor/output startup, Lua configuration, a mapped
Wayland terminal, all four packaged plugins loading/rendering/unloading, and
configuration reload. `runtime/desktop.py` adds wallpaper, screenshot capture,
idle timeout/resume, and a locked session rejecting a wrong password before a
successful PAM unlock. Screenshots, commands, process logs and `result.json`
are written inside the container to `/tmp/runtime-evidence`.

These tests require a Wayland socket and a GPU render node. The runtime
container shares only that display socket and render device; it does not receive
the host home, session/system D-Bus, credentials or DRM card device. Runtime
networking is disabled. SELinux labeling is disabled for this runtime container
so the existing socket and GPU can be used without relabeling the user's
session. Do not use this exception for untrusted source builds.

## Reproduce

From the repository root, select a fresh container/image suffix and the directory
containing the downloaded, signed candidate artifacts. That directory must hold
only the intended builds, arranged under `fedora-44-x86_64`/`fedora-45-x86_64`
subdirectories as produced by `copr-cli download-build`.

```bash
fedora=44                           # repeat with 45
candidate="$PWD/results/copr-2026-09-19.1"
prep="corp-runtime-prepare-$fedora"
nested="corp-runtime-test-$fedora"
runtime_image="localhost/corp-runtime-test:$fedora"
parent_socket="$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" # use absolute WAYLAND_DISPLAY directly
render_node=/dev/dri/renderD128    # inspect the actual host render nodes first

podman create --name "$prep" "localhost/corp-validation:f$fedora" sleep infinity
podman start "$prep"
podman cp scripts/runtime "$prep:/runtime-test"
podman cp "$candidate" "$prep:/candidate"
podman exec "$prep" bash /runtime-test/prepare.sh "$fedora"
```

Inspect the printed package NEVRAs against the release record before proceeding.
The preparation script replaces the minimal container's standalone tmpfiles
package with systemd to satisfy desktop service dependencies. It keeps COPR
signature checks on. Preparation needs network access; the following runtime
step does not. The `builder` user already exists in the validation image.

```bash
podman commit "$prep" "$runtime_image"
podman run --name "$nested" --network=none --userns=keep-id --user root \
  --device "$render_node" --security-opt label=disable \
  --mount "type=bind,src=$parent_socket,dst=/tmp/parent-wayland,ro=true" \
  -e WAYLAND_DISPLAY=/tmp/parent-wayland -e CORP_DESKTOP_TESTS=1 \
  "$runtime_image" bash -c '
    set -e
    echo builder:corp-runtime-only | chpasswd
    mkdir -p /run/dbus
    dbus-daemon --system --fork
    exec runuser -u builder -- dbus-run-session python3 /runtime-test/smoke.py
  '
podman cp "$nested:/tmp/runtime-evidence" "$candidate/desktop-evidence-$fedora"
```

The password above belongs only to the disposable container account and is used
by the test's virtual keyboard. Never apply it to a host account. Collect
evidence even if the test command fails, inspect `result.json` and the logs,
then remove only these objects:

```bash
podman rm -f "$nested" "$prep"
podman rmi "$runtime_image"
```

## Coverage and limits

A passing result exercises actual plugin linking and a client rendering while
each plugin is active. It does not verify every plugin feature (for example,
Counter-Strike custom Vulkan resolutions), every GPU, HDR or multi-monitor use.
Screen capture through `grim` does not prove portal/PipeWire screen sharing.
The private bus has no logind session, so suspend/inhibition and polkit prompts
need a separately provisioned desktop/VM. Do not count their absence as passes.

The 2026-09-19 tests passed on Fedora 44 and 45 with signed cursor/plugin
candidate RPMs and the existing public Hyprland 0.56.2-4. They used direct
`Hyprland` startup for debugging, so its expected `start-hyprland` warning was
visible; the minimal test image also lacked optional `hyprland-guiutils`.
Hypridle reported unavailable logind inhibition, while its timed and resumed
hooks passed. The full compositor logs also contain expected DRM/seat failures before
selecting the nested Wayland backend, an absent cursor theme falling back to
Xcursor, a missing fresh-user data directory, and no preferred nested output
mode. Config reload/plugin changes produced stale-watch notifications.
Hyprland logged missing color-description fallbacks during rendering and a
lock-surface destruction warning after unlock. The pinned source returns the
original color for that fallback; screenshots and the session remained usable.
No compositor crash or plugin ABI/unresolved-symbol failure occurred. These
diagnostics are retained in the evidence, not reported as clean logs.

Publication of this two-package maintenance update uses the scoped runtime
coverage above. Full portal/polkit, login/suspend and hardware qualification
remain follow-up coverage for the inherited stack; they are not represented as
completed by the nested test. The compositor, portal, locker and polkit RPMs
are unchanged by this release.
