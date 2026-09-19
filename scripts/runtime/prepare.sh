#!/bin/bash
# Run as root INSIDE a disposable Fedora validation container.
set -euo pipefail
[[ -e /run/.containerenv ]] || { echo 'Podman container required' >&2; exit 1; }
fedora=$1
[[ $fedora == 44 || $fedora == 45 ]]
curl -fsSL "https://copr.fedorainfracloud.org/coprs/dtutila/hyprland/repo/fedora-$fedora/dtutila-hyprland-fedora-$fedora.repo" -o /etc/yum.repos.d/hyprland.repo
dnf -y --setopt=timeout=30 --setopt=retries=3 swap systemd-standalone-tmpfiles systemd
dnf -y --setopt=timeout=30 --setopt=retries=3 install hyprland hyprland-plugins hyprcursor foot grim wtype hyprlock hypridle hyprpaper hyprpolkitagent xdg-desktop-portal-hyprland pipewire wireplumber dbus-daemon procps-ng polkit
mapfile -t candidate < <(find /candidate -type f -path "*/fedora-$fedora-x86_64/*" -name '*.rpm' ! -name '*.src.rpm' ! -name '*debuginfo*' ! -name '*debugsource*' | sort)
((${#candidate[@]} > 0))
rpm -K "${candidate[@]}"
dnf -y --setopt=localpkg_gpgcheck=1 install "${candidate[@]}"
dnf check
rpm -q hyprland hyprland-plugins hyprcursor hyprlock hypridle hyprpaper
