#!/bin/bash
# Prepare runtime dependencies only inside a task-created Fedora VM.
set -euo pipefail
test -f /etc/corp-test-vm
systemd-detect-virt --vm
dnf -y --setopt=timeout=30 --setopt=minrate=10000 --setopt=retries=3 upgrade
dnf -y --setopt=timeout=30 --setopt=minrate=10000 --setopt=retries=3 install foot grim wtype python3-gobject gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good pipewire-gstreamer pipewire wireplumber xdg-desktop-portal dbus-daemon procps-ng polkit nftables createrepo_c dnf5-plugins google-noto-sans-fonts
gst-inspect-1.0 pipewiresrc
install -d -m0755 /opt/corp-test
cat > /usr/share/polkit-1/actions/org.example.corp.runtime.policy <<'POLICY'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN" "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <action id="org.example.corp.runtime">
    <description>Disposable COPR runtime authentication check</description>
    <message>Authenticate for the disposable runtime test</message>
    <defaults>
      <allow_any>auth_self</allow_any>
      <allow_inactive>auth_self</allow_inactive>
      <allow_active>auth_self</allow_active>
    </defaults>
  </action>
</policyconfig>
POLICY
systemctl restart polkit
printf '%s\n' 'VM dependency preparation passed.'
