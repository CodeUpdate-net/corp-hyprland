#!/bin/bash
# Run as root only inside the task-created, signed-candidate Fedora VM.
set -euo pipefail
test -f /etc/corp-test-vm
systemd-detect-virt --vm
[[ $(id -u) == 0 ]]
test -f /opt/corp-test/smoke.py
id corp-test
# A bare tty login does not activate graphical-session.target. Give this
# disposable compositor fixture its own target, like a desktop session manager.
cat > /etc/systemd/user/corp-runtime-session.target <<'UNIT'
[Unit]
Description=Disposable COPR compositor runtime session
BindsTo=graphical-session.target
Before=graphical-session.target
UNIT
install -d -m0755 /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/corp-runtime.conf <<'UNIT'
[Service]
ExecStart=
ExecStart=-/usr/sbin/agetty --autologin corp-test --noclear %I $TERM
UNIT
cat > /home/corp-test/.bash_profile <<'PROFILE'
if [[ $(tty) == /dev/tty1 && ! -e /tmp/corp-runtime-started ]]; then
    touch /tmp/corp-runtime-started
    export XDG_CURRENT_DESKTOP=Hyprland XDG_SESSION_TYPE=wayland
    export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
    export CORP_NATIVE_VM=1 CORP_DESKTOP_TESTS=1 CORP_SESSION_TESTS=1
    exec python3 /opt/corp-test/smoke.py > /tmp/corp-session-test.log 2>&1
fi
PROFILE
chown corp-test:corp-test /home/corp-test/.bash_profile
# Keep only the private localhost SSH control channel and loopback traffic.
# No host network settings are changed.
nft delete table inet corp_runtime 2>/dev/null || true
nft add table inet corp_runtime
nft 'add chain inet corp_runtime output { type filter hook output priority 0; policy drop; }'
nft add rule inet corp_runtime output oifname lo accept
nft add rule inet corp_runtime output ip daddr 10.0.2.2 accept
systemctl daemon-reload
systemctl restart getty@tty1
