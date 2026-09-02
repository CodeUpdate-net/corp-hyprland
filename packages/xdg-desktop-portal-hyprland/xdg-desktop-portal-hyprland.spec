Name:           xdg-desktop-portal-hyprland
Version:        1.4.1
Release:        1%{?dist}
Summary:        XDG Desktop Portal backend for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/xdg-desktop-portal-hyprland
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  hyprwayland-scanner-devel >= 0.4.2
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprland-protocols)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3) >= 1.1.82
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0.0
BuildRequires:  pkgconfig(uuid)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  systemd-rpm-macros
Requires:       xdg-desktop-portal

%description
Screen sharing and related XDG Desktop Portal services for Hyprland.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  -DSYSTEMD_SERVICES=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprland-share-picker
%{_libexecdir}/xdg-desktop-portal-hyprland
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.hyprland.service
%{_datadir}/xdg-desktop-portal/portals/hyprland.portal
%{_userunitdir}/xdg-desktop-portal-hyprland.service

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 1.4.1-1
- Initial package
